# Using DICOM SCU on Azure Deployment

## Setup:
XNAT deployed using Azure Container instance using [arm template](../1_Deployment/arm/xnat.json)

* Size: Standard D4s v3 (4 vCPUs, 8 GiB memory)
* Azure file share mounted on container

## DataSet:
Source: Padchest Number of images used: 1000 Size of images:
```
Max size: 15 MB
Min size: 1.5 MB
Avg size: 6.2 MB
Median size: 3.6 MB
```


## Test:
We ran the following following script from a VM:
```
find . -name "*.dcm" | head -n1000 | xargs storescu -v --aetitle XNAT --call XNAT <xnat_address> 8104
``` 

## Result:
```
real	26m1.788s
user	0m2.257s
sys	0m7.182s
```

26 minutes to upload 1000 images.
