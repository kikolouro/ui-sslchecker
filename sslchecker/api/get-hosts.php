<?php
require('connect.php');
try {
    $stmt = $db->prepare('SELECT * FROM hosts order by host');
    $stmt->execute();
    $hosts = $stmt->fetchAll();
    echo json_encode($hosts);
} catch (PDOException $ex) {
    echo $ex;
    die;
}
