docker run -p 22:22 -p 25:25 -p 80:80 -p 456:456 -p 587:587 -p 110:110 -p 143:143 -p 993:993 -p 995:995 -p 443:443 -p 8080:8080 -p 8443:8443 -p 7071:7071 -p 9071:9071  -i -t -e PASSWORD=temp1234 -e EXT_HOST=zimbra -e EXT_DOMAIN=roselroa.net zimbra_centos