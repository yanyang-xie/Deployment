hosts=172.31.13.47,172.31.13.48
command="cd /usr/local/thistech/tomcat/webapps && rm -rf vex && scp -i ~/ttbj-keypair.pem root@172.31.13.165:/root/yifu/vex*.war vex.war && ls -al vex.war"

fab -i ~/ttbj-keypair.pem -P -H ${hosts}  -- "${command}"