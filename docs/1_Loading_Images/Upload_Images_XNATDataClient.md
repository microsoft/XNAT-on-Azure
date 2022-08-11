# Uploading images using XNAT data client

XnatDataClient, or XDC, is a command-line tool for making HTTP calls to an XNAT server. It's a command-line tool like cURL. 

# Installation
The XNATDataClient jar is available for download on this: [Download Link](https://bitbucket.org/xnatdev/data-client/downloads/)

#  Usage
```
$ export rest_params="-u <USERNAME> -p <PASSWORD>"
```

## Creating a subject
Following is how we'd create a subject with ID: `demosubjectusingxdc1` for our `demoproject`
```
$ java -jar XnatDataClient-1.7.6-all.jar $rest_params -m PUT -r http://localhost/data/projects/demoproject/subjects/demosubjectusingxdc1
```
Outputs something like:
```
XNAT02_S00004
```

## Creating a session

```
$ java -jar XnatDataClient-1.7.6-all.jar $rest_params -m PUT -r "http://localhost/data/projects/demoproject/subjects/demosubjectusingxdc1/experiments/session1?xnat:mrSessionData/date=01/24/22"
```
Should return something like:
```
XNAT02_E00004
```

## Creating a scan
```
java -jar XnatDataClient-1.7.6-all.jar $rest_params -m PUT -r "http://localhost/data/projects/demoproject/subjects/demosubjectusingxdc1/experiments/session1/scans/SCAN1?xsiType=xnat:mrScanData&xnat:mrScanData/type=T1"
```

```
java -jar XnatDataClient-1.7.6-all.jar $rest_params -m PUT -r "http://localhost/data/projects/demoproject/subjects/demosubjectusingxdc1/experiments/session1/scans/SCAN1/resources/DICOM?format=DICOM&content=T1_RAW" 
```

## Upload files for scan
Upload a file stored at `/images/PadChest/2.25.100018286306728784936917987616098917889/2.25.56044907757811046082233331445434988692/2.25.133737862600787998184561494911958442381.dcm` on local machine.

```
java -jar XnatDataClient-1.7.6-all.jar $rest_params -m PUT -r "http://localhost/data/projects/demoproject/subjects/demosubjectusingxdc1/experiments/session1/scans/SCAN1/resources/DICOM/files/1.dcm" -l /images/PadChest/2.25.100018286306728784936917987616098917889/2.25.56044907757811046082233331445434988692/2.25.133737862600787998184561494911958442381.dcm
```
