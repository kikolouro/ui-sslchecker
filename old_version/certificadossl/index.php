<?php
function curl($type, $data)
{

    $cURLConnection = curl_init("API URL/api/$type");
    if ($data != NULL) {
        curl_setopt($cURLConnection, CURLOPT_POSTFIELDS, $data);
    }
    curl_setopt($cURLConnection, CURLOPT_RETURNTRANSFER, true);
    $apiResponse = curl_exec($cURLConnection);
    curl_close($cURLConnection);
    return $apiResponse;
}
?>
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Certificados SSL</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    <script src="https://code.jquery.com/jquery-3.6.0.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.4.0/font/bootstrap-icons.css">
    <link rel="stylesheet" href="css/style.css">
</head>

<?php


if (isset($_REQUEST['submit'])) {
    $json = array(
        "newhost" => $_REQUEST['newhost']
    );
    echo curl("new-host.php", $json);


?>

    <script>
        var token;
        var id;
        if (window.XMLHttpRequest) {
            xmlhttp = new XMLHttpRequest();
        } else {
            xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
        }
        xmlhttp.onreadystatechange = () => {
            if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                aux = JSON.parse(xmlhttp.responseText);
                token = aux.result
                id = aux.id

                if (window.XMLHttpRequest) {
                    xmlhttp = new XMLHttpRequest();
                } else {
                    xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
                }
                xmlhttp.onreadystatechange = () => {
                    if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                        aux = xmlhttp.responseText;
                        if (window.XMLHttpRequest) {
                            xmlhttp = new XMLHttpRequest();
                        } else {
                            xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
                        }
                        xmlhttp.onreadystatechange = () => {
                            if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                                aux = xmlhttp.responseText;
                                window.location.replace("index.php");
                            }
                        }
                        xmlhttp.open("POST", "ZABBIX_SERVER_URL/zabbix/api_jsonrpc.php", true);
                        xmlhttp.setRequestHeader("Content-Type", "application/json")
                        xmlhttp.send(JSON.stringify({
                            "jsonrpc": "2.0",
                            "method": "trigger.create",
                            "params": [{
                                "description": "<?= $_REQUEST['newhost'] ?> falhou: {ITEM.VALUE}",
                                "expression": "{ZABBIX_SERVER_URL:web.test.error[<?= $_REQUEST['newhost'] ?>_cenario].strlen()}>0 and {ZABBIX_SERVER_URL:web.test.fail[<?= $_REQUEST['newhost'] ?>_cenario].last()}>0",
                                "priority": "5"

                            }, {
                                "description": "<?= $_REQUEST['newhost'] ?> está lento: {ITEM.VALUE}",
                                "expression": "{ZABBIX_SERVER_URL:web.test.in[<?= $_REQUEST['newhost'] ?>_cenario,,bps].last()}<500",
                                "priority": "5"

                            }],
                            "auth": token,
                            "id": id
                        }))
                    }
                }
                xmlhttp.open("POST", "ZABBIX_SERVER_URL/zabbix/api_jsonrpc.php", true);
                xmlhttp.setRequestHeader("Content-Type", "application/json")
                xmlhttp.send(JSON.stringify({
                    "jsonrpc": "2.0",
                    "method": "httptest.create",
                    "params": {
                        "name": "<?= $_REQUEST['newhost'] ?>_cenario",
                        "hostid": "10084",
                        "agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0",
                        "steps": [{
                            "name": "<?= $_REQUEST['newhost'] ?>",
                            "url": "https://<?= $_REQUEST['newhost'] ?>/",
                            "status_codes": "200,201,210-299,302",
                            "no": 1
                        }]
                    },
                    "auth": token,
                    "id": id
                }));
            }

        }

        xmlhttp.open("POST", "ZABBIX_SERVER_URL/zabbix/api_jsonrpc.php", true);
        xmlhttp.setRequestHeader("Content-Type", "application/json")
        xmlhttp.send(JSON.stringify({
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": "ZABBIX_USER",
                "password": "ZABBIX_USER_PASSWORD"
            },
            "id": 1,
            "auth": null
        }));
    </script>
<?php

}

if (isset($_REQUEST['runscript'])) {
    $output .= shell_exec(escapeshellcmd('python3 /etc/sslchecker/ssl_checker.py -db'));
}

if (isset($_REQUEST['edit'])) {
    $json = array(
        "newhost" => $_REQUEST['editedhost'],
        "id" => $_REQUEST['host']
    );
    curl("edit-host.php", $json);
    header("LOCATION: index.php");
}

if (isset($_REQUEST['import'])) {
    $uploaddir = '/var/www/sslchecker/uploads/';
    $uploadfile = $uploaddir . "temp";
    if (copy($_FILES['file']['tmp_name'], $uploadfile)) {
        $json = array(
            "file" => "@" . $_FILES['file']['tmp_name']
        );

        echo curl("import-from-file.php", $json);
    } else {
        echo "Possível ataque de upload de arquivo!\n";
    }


    header("LOCATION: index.php");
}
if (isset($_REQUEST['delete'])) {
    $json = array(
        "id" => $_REQUEST['id']
    );
    $host = curl("delete-host.php", $json);


?>
    <script>
        var token;
        var id;
        if (window.XMLHttpRequest) {
            xmlhttp = new XMLHttpRequest();
        } else {
            xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
        }

        xmlhttp.onreadystatechange = () => {
            if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                aux = JSON.parse(xmlhttp.responseText);
                token = aux.result
                id = aux.id

                if (window.XMLHttpRequest) {
                    xmlhttp = new XMLHttpRequest();
                } else {
                    xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
                }
                xmlhttp.onreadystatechange = () => {
                    if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                        aux = JSON.parse(xmlhttp.responseText);
                        json = {
                            "jsonrpc": "2.0",
                            "method": "trigger.delete",
                        }
                        json.params = []
                        aux.result.forEach((self) => {
                            json.params.push(self.triggerid)
                        })
                        json.auth = token
                        json.id = id
                        if (window.XMLHttpRequest) {
                            xmlhttp = new XMLHttpRequest();
                        } else {
                            xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
                        }
                        xmlhttp.onreadystatechange = () => {
                            if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                                aux = JSON.stringify(xmlhttp.responseText);
                                if (window.XMLHttpRequest) {
                                    xmlhttp = new XMLHttpRequest();
                                } else {
                                    xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
                                }
                                xmlhttp.onreadystatechange = () => {
                                    if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                                        aux = JSON.parse(xmlhttp.responseText);
                                        temp = aux.result[0].httptestid
                                        if (window.XMLHttpRequest) {
                                            xmlhttp = new XMLHttpRequest();
                                        } else {
                                            xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
                                        }
                                        xmlhttp.onreadystatechange = () => {
                                            if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
                                                window.location.replace("index.php");
                                            }
                                        }
                                        xmlhttp.open("POST", "ZABBIX_SERVER_URL/zabbix/api_jsonrpc.php", true);
                                        xmlhttp.setRequestHeader("Content-Type", "application/json")
                                        xmlhttp.send(JSON.stringify({
                                            "jsonrpc": "2.0",
                                            "method": "httptest.delete",
                                            "params": {
                                                "httptestid": temp
                                            },
                                            "auth": token,
                                            "id": id
                                        }));
                                    }
                                }
                                xmlhttp.open("POST", "ZABBIX_SERVER_URL/zabbix/api_jsonrpc.php", true);
                                xmlhttp.setRequestHeader("Content-Type", "application/json")
                                xmlhttp.send(JSON.stringify({
                                    "jsonrpc": "2.0",
                                    "method": "httptest.get",
                                    "params": {
                                        "output": [
                                            "httptestid"
                                        ],
                                        "selectFunctions": "extend",
                                        "filter": {
                                            "name": "<?= $host ?>_cenario"
                                        }
                                    },
                                    "auth": token,
                                    "id": id
                                }));

                            }

                        }
                        xmlhttp.open("POST", "ZABBIX_SERVER_URL/zabbix/api_jsonrpc.php", true);
                        xmlhttp.setRequestHeader("Content-Type", "application/json")
                        xmlhttp.send(JSON.stringify(json));

                    }
                }
                xmlhttp.open("POST", "ZABBIX_SERVER_URL/zabbix/api_jsonrpc.php", true);
                xmlhttp.setRequestHeader("Content-Type", "application/json")
                xmlhttp.send(JSON.stringify({
                    "jsonrpc": "2.0",
                    "method": "trigger.get",
                    "params": {
                        "hostsid": "10084",
                        "output": [
                            "triggersid"
                        ],
                        "selectFunctions": "extend",
                        "filter": {
                            "description": [
                                "<?= $host ?> está lento: {ITEM.VALUE}",
                                "<?= $host ?> falhou: {ITEM.VALUE}"
                            ]
                        }
                    },
                    "auth": token,
                    "id": id
                }));

            }
        }
        xmlhttp.open("POST", "ZABBIX_SERVER_URL/zabbix/api_jsonrpc.php", true);
        xmlhttp.setRequestHeader("Content-Type", "application/json")
        xmlhttp.send(JSON.stringify({
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": "ZABBIX_USER",
                "password": "ZABBIX_USER_PASSWORD"
            },
            "id": 1,
            "auth": null
        }));
    </script>
<?php

}
if (isset($_REQUEST['export'])) {
    shell_exec('python3 /etc/sslchecker/database_to_file.py');
    shell_exec('cp /var/www/sslchecker/hosts /var/www/certificadossl/');
    $File = 'hosts';
    $quoted = sprintf('"%s"', addcslashes(basename($File), '"\\'));
    $size   = filesize($file);
    header('Content-Description: File Transfer');
    header('Content-Type: application/octet-stream');
    header('Content-Disposition: attachment; filename=' . $quoted);
    header('Content-Transfer-Encoding: binary');
    header('Connection: Keep-Alive');
    header('Expires: 0');
    header('Cache-Control: must-revalidate, post-check=0, pre-check=0');
    header('Pragma: public');
    header('Content-Length: ' . $size);
}
$hosts = json_decode(curl("get-hosts.php", null));
?>


<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark static-top">
        <div class="container">
            <a class="navbar-brand" href="#">
                <img src="LOGO" width="30%" alt="">
            </a>
            <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarResponsive" aria-controls="navbarResponsive" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarResponsive">
                <ul class="navbar-nav ml-auto">
                    <li class="nav-item">
                        <a download="hosts" class="nav-link" href="hosts">Exportar ficheiro de hosts</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" data-toggle="modal" data-target="#import" id="importbutton" href="#">Importar ficheiro de hosts</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    <div class="container">
        <div class="row">
            <div class="col-6" align="center">
                <h1>Hosts</h1>
                <ul class="list-group" id="hosts">
                    <?php
                    foreach ($hosts as $key => $value) {
                    ?>
                        <li id="host<?= $value->id ?>" class="list-group-item">

                            <div class="container">
                                <h6 id="dns<?= $value->id ?>"><?= $value->host ?>
                                    <!--<i id="hostpencil<?= $value->id ?>" style="color:#d1ac47" class="bi bi-pencil"></i>--><i id="hostcross<?= $value->id ?>" style="color:#8f2214" class="bi bi-x-circle"></i>
                                </h6>
                                <form method="POST" action="index.php?edit&host=<?= $value->id ?>">
                                    <!--<div class="input-group">
                                        <input class="form-control" name="editedhost" id="input<?= $value->id ?>" type="hidden" value="<?= $value->host ?>" placeholder="<?= $value->host ?>" />
                                        <div id="button<?= $value->id ?>" class="input-group-append">
                                            <button type="submit" class="btn btn-primary">Editar</button>
                                            <button id="Sair<?= $value->id ?>" type="button" class="btn btn-danger">Sair</button>
                                        </div>
                                    </div>-->
                                </form>
                            </div>
                        </li>
                        <div class="modal fade" id="delete<?= $value->id ?>" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabel" aria-hidden="true">
                            <div class="modal-dialog" role="document">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <h5 class="modal-title" id="exampleModalLabel">Apagar <?= $value->host ?>?</h5>
                                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                            <span aria-hidden="true">&times;</span>
                                        </button>
                                    </div>
                                    <form action="index.php?delete" method="POST">
                                        <div class="modal-body">
                                            <input type="text" id="deleteinput<?= $value->id ?>" class="form-control" placeholder="Nome do host a apagar" />
                                            <input type="hidden" name="id" value="<?= $value->id ?>" />
                                        </div>
                                        <div class=" modal-footer">
                                            <button type="button" class="btn btn-secondary active" data-dismiss="modal">Voltar atrás</button>
                                            <button type="submit" id="deletebutton<?= $value->id ?>" class="btn btn-danger" disabled>Apagar <?= $value->host ?></button>

                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                        <script>
                            $('#host<?= $value->id ?>').hover(() => {
                                $('#hostpencil<?= $value->id ?>').removeClass('bi-pencil')
                                $('#hostpencil<?= $value->id ?>').addClass('bi-pencil-fill')
                                $('#hostcross<?= $value->id ?>').removeClass('bi-x-circle')
                                $('#hostcross<?= $value->id ?>').addClass('bi-x-circle-fill')
                            }, () => {
                                $('#hostpencil<?= $value->id ?>').removeClass('bi-pencil-fill')
                                $('#hostpencil<?= $value->id ?>').addClass('bi-pencil')
                                $('#hostcross<?= $value->id ?>').removeClass('bi-x-circle-fill')
                                $('#hostcross<?= $value->id ?>').addClass('bi-x-circle')
                            })

                            $('#hostpencil<?= $value->id ?>').click(() => {
                                $('#input<?= $value->id ?>').attr('type', 'text')
                                $('#dns<?= $value->id ?>').hide()
                                $('#button<?= $value->id ?>').show()
                            })
                            $('#Sair<?= $value->id ?>').click(() => {
                                $('#input<?= $value->id ?>').attr('type', 'hidden')
                                $('#dns<?= $value->id ?>').show()
                                $('#button<?= $value->id ?>').hide()
                            })
                            $('#hostcross<?= $value->id ?>').click(() => {
                                $('#delete<?= $value->id ?>').modal()
                            })
                            $('#deleteinput<?= $value->id ?>').keyup(() => {
                                if ($('#deleteinput<?= $value->id ?>').val() == '<?= $value->host ?>')
                                    document.getElementById('deletebutton<?= $value->id ?>').disabled = false
                                else
                                    document.getElementById('deletebutton<?= $value->id ?>').disabled = true
                            })
                        </script>
                    <?php
                    }
                    ?>
                </ul>
            </div>
            <div class="col-6" align="center">
                <h1>Novo Host</h1>
                <form action="index.php?submit=" method="POST">
                    <input class="form-control" type="text" name="newhost" placeholder="Novo Host" /><br>
                    <button class="form-control btn btn-primary" type="Submit">Adicionar</button>
                </form>
            </div>
        </div>
        <br>
        <div class="row">
            <div class="col-3" align="center">
                <h1>Correr Script</h1>
                <a href="index.php?runscript" class="form-control btn btn-primary" type="submit">Correr Script</a>
            </div>

            <div class="col-9" align="center">
                <h1>Output</h1>
                <textarea class="form-control" rows="15" cols="50" id="textarea" readonly><?= $output ?></textarea>
            </div>
        </div>
    </div>
    <div class="modal fade" id="import" tabindex="-1" role="dialog" aria-labelledby="import" aria-hidden="true">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="exampleModalLabel">Arrasta o ficheiro novo</h5>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <form action="index.php?import" method="POST" enctype="multipart/form-data">
                    <div class="modal-body">
                        <input type="file" name="file" class="form-control" />
                    </div>
                    <div class=" modal-footer">
                        <button type="button" class="btn btn-secondary active" data-dismiss="modal">Voltar atrás</button>
                        <button type="submit" class="btn btn-danger">Importar</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    <script>
        $(document).ready(() => {
            $('.input-group-append').hide()
        })
    </script>
    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>
</body>

</html>