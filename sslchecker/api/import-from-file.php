<?php
require('connect.php');
$hosts = file('../uploads/temp');
print_r($hosts);
$regexp = '/^(?:[-A-Za-z0-9]+\.)+[A-Za-z]{2,6}$/';
$hostsformatted = '';
foreach ($hosts as $key => $value) {
    if (0 == preg_match($regexp, $value)) {
        echo ('Erro de syntax no ficheiro ou host inválido.');
        die;
    }
    $hostsformatted .= ' ("' . substr($value, 0, -1) . '"),';
}
//echo $hostsformatted;
try {
    $stmt = $db->prepare('TRUNCATE TABLE hosts');
    $stmt->execute();
    $stmt = $db->prepare('INSERT INTO hosts (host) VALUES ' . substr($hostsformatted, 1, -1));
    $stmt->execute();
} catch (PDOException $ex) {
    echo $ex;
}
