# SSLCHECKER 
##### Aplicação para verificar certificados SSL e adicionar hosts no Zabbix (Zabbix server já configurado)

***Ficheiros e localizações***
- ssl_checker.py: /etc/sslchecker ;
- requirements.txt: /etc/sslchecker ;
- sslchecker(pasta): /var/www (Virtualhost sslcheckerapi.pacsis.org);
- certificadossl(pasta): /var/www (Virutalhost certificadossl.pacsis.org);
- schema.sql: /etc/sslchecker . 
***Instalação***
- Primeiro criar dois virutal hosts no apache (seguir tutorial na [digitalocean] (https://www.digitalocean.com/community/tutorials/como-configurar-apache-virtual-hosts-no-ubuntu-16-04-pt)).
- Instalar python3, caso não esteja instalado: `sudo apt install python3.8`.
- Colocar os ficheiros nas suas localizações.
- Instalar bibliotecas necessárias: 
```
cd /etc/sslchecker 
pip3 install -r requirements.txt
```
- Instalar mysql, caso não esteja instalado: (https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-20-04-pt)
- Criar base de dados:
```
cd /etc/sslchecker
mysql -u root -p
*Password de mysql do utilizador root*
source shcema.sql
```
- Criar utilizador mysql e garantir previlégios à nova base de dados:
```
CREATE USER 'certificadossl'@'localhost' IDENTIFIED BY '*password*';
GRANT ALL PRIVILEGES ON certificadossl. * TO 'certificados'@'localhost';
```
- Substituir passwords: 
    - mysql
        - /etc/sslchecker/sslchecker.py: `linha 408: pw = "*password*"`
        - /var/www/sslchecker/api/connect.php: `linha 5: $sPassword = "*password*"`
    - email
        - /var/www/sslchecker/api/mandar-email.php: `linha 12: $mail->Password = "*password*"`