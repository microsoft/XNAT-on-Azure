#!/bin/sh

/usr/sbin/sshd

mkdir -p ${XNAT_ROOT}/archive \
        ${XNAT_ROOT}/build \
        ${XNAT_ROOT}/cache \
        ${XNAT_ROOT}/ftp \
        ${XNAT_ROOT}/pipeline \
        ${XNAT_ROOT}/prearchive \
	      ${XNAT_HOME}/config \
        ${XNAT_HOME}/logs \
        ${XNAT_HOME}/plugins \
        ${XNAT_HOME}/work


export PGPASSWORD=$XNAT_DATASOURCE_PASSWORD
# generate xnat config
if [ ! -f $XNAT_HOME/config/xnat-conf.properties ]; then
  cat > $XNAT_HOME/config/xnat-conf.properties << EOF
datasource.driver=$XNAT_DATASOURCE_DRIVER
datasource.url=$XNAT_DATASOURCE_URL
datasource.username=$XNAT_DATASOURCE_USERNAME
datasource.password=$XNAT_DATASOURCE_PASSWORD

hibernate.dialect=org.hibernate.dialect.PostgreSQL9Dialect
hibernate.hbm2ddl.auto=update
hibernate.show_sql=false
hibernate.cache.use_second_level_cache=true
hibernate.cache.use_query_cache=true

spring.http.multipart.max-file-size=1073741824
spring.http.multipart.max-request-size=1073741824
EOF
fi

cp /root/ohif-viewer.jar ${XNAT_HOME}/plugins/ohif-viewer.jar

if [ ! -z "$XNAT_EMAIL" ]; then
  cat > $XNAT_HOME/config/prefs-init.ini << EOF
[siteConfig]
adminEmail=$XNAT_EMAIL
EOF
fi

if [ "$XNAT_SMTP_ENABLED" = true ]; then
  cat >> $XNAT_HOME/config/prefs-init.ini << EOF
[notifications]
smtpEnabled=true
smtpHostname=$XNAT_SMTP_HOSTNAME
smtpPort=$XNAT_SMTP_PORT
smtpUsername=$XNAT_SMTP_USERNAME
smtpPassword=$XNAT_SMTP_PASSWORD
smtpAuth=$XNAT_SMTP_AUTH
EOF
fi

mkdir -p /usr/local/share/xnat
find $XNAT_HOME/config -mindepth 1 -maxdepth 1 -type f -exec cp {} /usr/local/share/xnat \;
sed -i -e 's/8080/80/' ${CATALINA_HOME}/conf/server.xml
set -e

cmd="$@"
echo "Connecting psql @ $XNAT_DATASOURCE_HOST"
until psql -U "$XNAT_DATASOURCE_USERNAME" -d "$XNAT_DATASOURCE_DBNAME" -h "$XNAT_DATASOURCE_HOST" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 5
done

>&2 echo "Postgres is up - executing command \"$cmd\""
exec $cmd

