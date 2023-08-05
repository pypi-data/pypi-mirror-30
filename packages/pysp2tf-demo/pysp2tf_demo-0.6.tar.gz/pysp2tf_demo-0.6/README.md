## INTRODUCTION

This prototype illustrates how to use Spark and TensorFlow in Python

##  Apply Spark to analyze AMAZON BIN IMAGE DATASETS 

AMAZON BIN Image Dataset is located at S3 bucket aft-vbi-pds (https://aws.amazon.com/public-datasets/amazon-bin-images/).
We apply [ds_select.py](https://github.com/anfeng/py-demo/blob/master/py2tf/ds_select.py) to use PySpark API to  
extract, query and transform datasets, and finally save the result subdataset in TensorFlow Record format on my S3 bucket.   

```
pip install pysp2tf-demo
export PYSP2TF=/usr/local/lib/python2.7/site-packages/py2tf
spark-submit --jars $PYSP2TF/jars/hadoop-aws-2.7.5.jar,$PYSP2TF/jars/aws-java-sdk-1.7.4.jar,$PYSP2TF/jars/spark-tensorflow-connector_2.11-1.6.0.jar $PYSP2TF/ds_select.py tfsp-andyf
```

The log will include the following section about the newly created dataset.

```
+----------+--------------------+----+------------------+----+---------------+------+-------------------+--------+
|      asin|                name|unit|             value|unit|          value|  unit|              value|quantity|
+----------+--------------------+----+------------------+----+---------------+------+-------------------+--------+
|B01EM75DEO|Little Artist- Pa...|  IN|     0.99999999898|  IN|11.749999988015|pounds|0.14999999987421142|       2|
|B00VVLEKY4|Lacdo 13-13.3 Inc...|  IN|     1.49999999847|  IN| 13.99999998572|pounds|               0.25|       3|
|B00TKQEZV0|Enimay Hookah Hos...|  IN|    2.599999997348|  IN|13.199999986536|pounds|               0.25|       5|
|B01DV2OJYG|Best Microfiber C...|  IN|     5.99999999388|  IN| 11.99999998776|pounds| 1.8999999984066778|       3|
|B013HWXMJS|DocBear Bathroom ...|  IN|1.3999999985719997|  IN| 15.99999998368|pounds| 0.3499999997064932|       2|
|B00VXEWR6W|Full Body Moistur...|  IN|     3.49999999643|  IN| 3.899999996022|pounds|  1.410944074725587|       3|
|B01BBGYN0O|Simplicity Women'...|  IN|    2.899999997042|  IN|15.599999984088|pounds| 0.5499999995387752|       3|
|1629054755|Horses Wall Calen...|  IN|     0.42913385783|  IN| 13.38188975013|pounds|    0.6999897280762|       2|
|B00T3ROXI6|AmazonBasics Clea...|  IN|    1.249999998725|  IN| 11.49999998827|pounds| 1.6499999986163254|       3|
+----------+--------------------+----+------------------+----+---------------+------+-------------------+--------+
```

## Python Packaging

```
rm -r dist/*
python setup.py sdist bdist_wheel 
twine upload dist/*

pip install pysp2tf-demo
```
