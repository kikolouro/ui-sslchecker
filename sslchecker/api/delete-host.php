<?php
require('connect.php');
$id = $_REQUEST['id'];
try {
    $stmt = $db->prepare('SELECT host from hosts where id = :id');
    $stmt->bindValue(':id', $id);
    $stmt->execute();
    $arr = $stmt->fetchAll();
    echo $arr[0]->host;
    $stmt = $db->prepare('DELETE FROM hosts WHERE id = :id');
    $stmt->bindValue(':id', $id);
    $stmt->execute();
} catch (PDOException $ex) {
    echo $ex;
    die;
}
