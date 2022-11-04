# XNAT on Azure
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fgithub.com%2Fmicrosoft%2FXNAT-on-Azure%2Fblob%2Fmain%2Fsrc%2Farm%2Fxnat.ui.json)

The goal of this repository is to provide code, templates and best practices for deploying [XNAT](https://xnat.org/about/) on Azure. 


# Overview
![xnat overview](./images/XNAT%20Diagrams.jpg)


The repository is organized in `src` and `docs` directory. The `src` directory contains code for building the docker container and ARM templates. The `docs` directory contains the following:

1. [Loading Images](./docs/1_Loading_Images/README.md)
2. [Setting up a project](./docs/2_Setting_up_project/README.md)
3. [Programmatic access to data](./docs/3_Programmatic_Access/README.md)
4. [Training ML Model on Azure ML](./docs/4_Training_Model_On_Azure_ML/README.md)

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
