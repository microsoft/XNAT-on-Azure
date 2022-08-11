# Upload using DICOM StoreSCU

XNAT includes an integreated DICOM C-Store Class provider. Any DICOM service is a transaction between 2 entities:
1. An SCU that initiates the request
2. SCP that responds

In our [deployment]((../1_Deployment/README.md)) we configure the XNAT DICOM port at `8104` and AETitle as `XNAT`


Following is an example using [DCMTK's](https://dcmtk.org/) `storescu`  command line utility
```
storescu -v --aetitle XNAT --call XNAT <your_xnat_addres> 8104  <your_image.dcm>
```

Please Note: This step pushes images into the [prearchive](https://wiki.xnat.org/documentation/how-to-use-xnat/image-session-upload-methods-in-xnat/using-the-prearchive). The studies must then be archived and moved to a project.