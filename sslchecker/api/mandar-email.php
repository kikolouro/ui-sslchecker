<?php
require 'PHPMailer/PHPMailerAutoload.php';

$mail = new PHPMailer;
$valid_days_to_expire = $_POST['valid_days_to_expire'];
$host = $_POST['host'];
$mail->Host = 'SMTP SERVER URL';
$mail->Port = 465;
$mail->SMTPAuth = true;
$mail->SMTPSecure = 'tls';
$mail->Username = 'EMAIL@EMAIL';
$mail->Password = 'PASSWORD';
$mail->setFrom('EMAIL@EMAIL');
$email = "EMAIL TO SEND TO";
$mail->CharSet = 'UTF-8';
$mail->addAddress($email);
$mail->addReplyTo($email);
$mail->isHTML(true);



if ($valid_days_to_expire < 0) {
    $mail->Subject = "Certificado expirou no host: $host";
    $mail->Body = "O certificado expirou no host: $host. Expirou a $valid_days_to_expire Dias";
} else {
    $mail->Subject = "Certificado a expirar no host: $host";
    $mail->Body = "O certificado está a expirar no host: $host. Falta $valid_days_to_expire Dias.";
}

if (!$mail->send()) {
    $res = "Alguma coisa não correu como esperado. Tente novamente";
}
