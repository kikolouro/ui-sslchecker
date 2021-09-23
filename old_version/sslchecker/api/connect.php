<?php
//ini_get('display_errors', 1);
try {
    $sUserName = 'USER';
    $sPassword = 'PASSWORD';
    $sConnection = "mysql:host=localhost; dbname=DBNAME; charset=utf8mb4";

    // PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
    $aOptions = array(
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_OBJ
    );
    $db = new PDO($sConnection, $sUserName, $sPassword, $aOptions);
} catch (PDOException $e) {
    echo $e;
    exit();
}
