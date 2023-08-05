#!/usr/bin/python

import os
import uuid
import sys
import boto3
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit

def mkDataFrame(spark, boto3_session): 
  s3 = boto3_session.resource('s3')
  bucket = s3.Bucket('aft-vbi-pds') 
  rdd = None
  for obj in bucket.objects.filter(Prefix='metadata/10000'):
    if obj.key.endswith('.json'):
      data=spark.read.json('s3n://aft-vbi-pds/'+obj.key,multiLine=True)
      data = data.withColumn('key', lit(str(obj.key)))
      sub_rdd = data.rdd.filter(lambda r: r.EXPECTED_QUANTITY>0).flatMap(lambda r: r.BIN_FCSKU_DATA).cache()
      if rdd is None:
         rdd = sub_rdd
      else:
         rdd = rdd.union(sub_rdd).cache()     
  return spark.createDataFrame(rdd)

bukcet = sys.argv[1]
if len(sys.argv)>=5:
  aws_region =  sys.argv[2]
  aws_access_key = sys.argv[3]
  aws_screte_key = sys.argv[4]
else:
  aws_region = os.environ['AWS_REGION']
  aws_access_key = os.environ['AWS_ACCESS_KEY_ID']
  aws_screte_key = os.environ['AWS_SECRET_ACCESS_KEY']

# set up Spark sessiom
spark = SparkSession.builder.appName("PySpark-TF example") \
  .config("spark.hadoop.fs.s3n.impl", "org.apache.hadoop.fs.s3native.NativeS3FileSystem") \
  .config("spark.hadoop.fs.s3n.readahead.range", "512M") \
  .config("spark.hadoop.fs.s3n.awsAccessKeyId", aws_access_key) \
  .config("spark.hadoop.fs.s3n.awsSecretAccessKey", aws_screte_key) \
  .getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# Acceess an existing dataset
boto3_session = boto3.session.Session(region_name=aws_region, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_screte_key)
df = mkDataFrame(spark, boto3_session)
df.show()

# perform a SQL based datas selection & transformation
df.createOrReplaceTempView('df')
new_data_set=spark.sql("SELECT asin, name, height.unit, height.value, length.unit, length.value, weight.unit, weight.value, quantity  FROM df WHERE height.value*length.value>5.0 and quantity>1").distinct()
new_data_set.show()

# Save selected/transformed dataset as TensorFlow Record format
new_data_set.repartition(2).write.format("tfrecords") \
            .save('s3n://'+bukcet+'/aft-vbi-pds-tfrecords/'+uuid.uuid1().hex)
