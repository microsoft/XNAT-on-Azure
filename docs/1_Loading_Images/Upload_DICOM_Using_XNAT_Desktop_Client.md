
# Upload DICOMs Using XNAT desktop Client

The XNAT desktop client is a GUI application which lets users interact with the XNAT server ([Download Link](https://download.xnat.org/desktop-client/)). We'll be using XNAT desktop client to connect to our XNAT server and upload DICOM images from local hard disk.

1. Open XNAT Desktop Client
![image.png](./images/image-96e0cf23-04c6-4b7a-a6a0-5d55e2f34177.png)

2. Click the "Add New XNAT Server" and fill in details of your XNAT server. For this tutorial we're connecting to XNAT server deployed on `10.2.0.9`
![image.png](./images/image-4b11d833-eae0-4ea1-b5e6-e67cd64a3d31.png)

3. Once you've successfully logged in you should see the following screen:
![image.png](./images/image-d12bc1c1-e9b3-4f7c-9d28-8a5de24ef35a.png)

4. Click "Upload files" button and select the desired project. For this tutorial we're using "Demo Project" as our project. You'll then be prompted to select an existing subject or to create a new subject.
![image.png](./images/image-026f60bf-5b87-4760-b63e-d345667e37c6.png)

5. Click next and then select the folder from your disk where the DICOM files are stored
![file_explorer.png](./images/file_explorer-8f186c9e-699d-476b-be70-66816efdd464.png)

6. Review the files that were uploaded
![image.png](./images/image-bc77e675-0550-419a-882b-ba255f1fe459.png)

7. The XNAT desktop client also comes with an embedded DICOM viewer to visually inspect the images to make sure there's no PHI in the pixel data.
![image.png](./images/image-b274f358-a6a0-4a37-8cdc-d31c581fe69b.png)

8. Click "Finish and Upload" and the images should be uploaded to the project
