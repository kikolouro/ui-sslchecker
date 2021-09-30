<?php
require('connect.php');
$newhost = $_REQUEST['newhost'];
$regexp = '/^(?:[-A-Za-z0-9]+\.)+[A-Za-z]{2,6}$/';
if (0 == preg_match($regexp, $newhost)) {
    echo ('Erro');
    die;
}
try {
    $stmt = $db->prepare('INSERT INTO hosts (host) VALUES (:host)');
    $stmt->bindValue(':host', $newhost);
    $stmt->execute();
} catch (PDOException $ex) {
    echo $ex;
    die;
}
