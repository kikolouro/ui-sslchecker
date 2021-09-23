<?php
require 'PHPMailer/PHPMailerAutoload.php';

$mail = new PHPMailer;
$mail->Host = 'smtp.gmail.com';
$mail->Port = 465;
$mail->SMTPAuth = true;
$mail->SMTPSecure = 'tls';
$mail->Username = 'joyn01.servicedesk@gmail.com';
$mail->Password = 'js9823!Xhf78#Q2';
$mail->setFrom('joyn01.servicedesk@gmail.com');
$email = "servicedesk@infosistema.com";
$mail->CharSet = 'UTF-8';
$mail->addAddress($email);
$mail->addReplyTo($email);
$mail->isHTML(true);

$mail->Subject = "TESTEFL";
$mail->Body = "TESTEFL";

if (!$mail->send()) {
    print_r($mail);
}
