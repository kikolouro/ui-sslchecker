<?php
require('connect.php');
$newhost = $_REQUEST['newhost'];
$id = $_REQUEST['id'];
$regexp = '/^(?:[-A-Za-z0-9]+\.)+[A-Za-z]{2,6}$/';
if (0 == preg_match($regexp, $newhost)) {
    echo ('Erro');
    die;
}
try {
    $stmt = $db->prepare('UPDATE hosts SET host=:newhost WHERE id=:id');
    $stmt->bindValue(':newhost', $newhost);
    $stmt->bindValue(':id', $id);
    $stmt->execute();
} catch (PDOException $ex) {
    echo $ex;
    die;
}
