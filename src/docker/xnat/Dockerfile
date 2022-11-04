FROM tomcat:9-jdk8-openjdk-buster

ARG XNAT_VERSION=1.8.3
ARG XNAT_OHIF_VERSION=3.1.0-XNAT-1.8.0
ARG XNAT_ROOT=/data/xnat
ARG XNAT_HOME=/data/xnat/home

ARG TOMCAT_XNAT_FOLDER=ROOT
ARG TOMCAT_XNAT_FOLDER_PATH=${CATALINA_HOME}/webapps/${TOMCAT_XNAT_FOLDER}

RUN apt-get update && apt-get install -y postgresql-client-11 wget 
RUN rm -rf ${CATALINA_HOME}/webapps/*
RUN mkdir -p ${TOMCAT_XNAT_FOLDER_PATH}

RUN wget --no-verbose --output-document=/tmp/xnat-web-${XNAT_VERSION}.war https://api.bitbucket.org/2.0/repositories/xnatdev/xnat-web/downloads/xnat-web-${XNAT_VERSION}.war
RUN unzip -o -d ${TOMCAT_XNAT_FOLDER_PATH} /tmp/xnat-web-${XNAT_VERSION}.war
RUN rm -f /tmp/xnat-web-${XNAT_VERSION}.war
 
RUN wget --no-verbose --output-document=/root/ohif-viewer.jar https://bitbucket.org/icrimaginginformatics/ohif-viewer-xnat-plugin/downloads/ohif-viewer-${XNAT_OHIF_VERSION}.jar 

# HTTP Port
EXPOSE 80

# DICOM Port
EXPOSE 8104

ENV XNAT_ROOT=${XNAT_ROOT} XNAT_HOME=${XNAT_HOME} XNAT_DATASOURCE_USERNAME=${XNAT_DATASOURCE_USERNAME} PGPASSWORD=${XNAT_DATASOURCE_PASSWORD}
ADD run.sh /usr/local/bin/run.sh

CMD ["/usr/local/bin/run.sh", "/usr/local/tomcat/bin/catalina.sh", "run"]
