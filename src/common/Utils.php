<?php

/**
 * A shortcut to get application instance.
 * @return \yii\Application
 */
function app() {
    return \Yii::$app;
}

/**
 * A shortcut to get application params.
 */
function param($name) {
    return \Yii::$app->params[$name];
}

/**
 * VarDumper is intended to replace the buggy PHP function var_dump and print_r.
 */
function dump($target) {
    return yii\helpers\VarDumper::dump($target, 10, true);
}

/**
 * Create url by urlManager.
 */
function url($params, $absolute = false) {
    if ($absolute) {
        return \Yii::$app->urlManager->createAbsoluteUrl($params);
    }
    return \Yii::$app->urlManager->createUrl($params);
}

/**
 * @return \yii\db\Command
 */
function sql($sql = null) {
    $connection = \Yii::$app->db;
    $command = $connection->createCommand($sql);
    
    return $command;
}

/**
 * Make http request via curl
 */
function curl($url, $method = 'GET', $postData = null, 
    $connectTime = 10, $runningTime = 0) {
    $data['error'] = null;

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, FALSE);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, FALSE);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, 1);
    curl_setopt($ch, CURLOPT_AUTOREFERER, 1);
    curl_setopt($ch,CURLOPT_TIMEOUT, $runningTime);  // timeout for request
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, $connectTime);  // timeout for connection
    if ($method == 'POST' && $postData != null) {
        curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
    }
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $data['response'] = curl_exec($ch);
    if (curl_errno($ch)) {
        $data['error'] = curl_error($ch);
    }
    curl_close($ch);

    return $data;
}

function curl_wx_ssl($url, $vars) {
    $ch = curl_init();
    curl_setopt($ch,CURLOPT_TIMEOUT, 30);  // timeout for request
    curl_setopt($ch,CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch,CURLOPT_URL, $url);
    curl_setopt($ch,CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch,CURLOPT_SSL_VERIFYHOST, false);
    curl_setopt($ch,CURLOPT_SSLCERTTYPE, 'PEM');
    curl_setopt($ch,CURLOPT_SSLCERT, realpath('./pay/wxpay/apiclient_cert.pem'));
    curl_setopt($ch,CURLOPT_SSLKEYTYPE, 'PEM');
    curl_setopt($ch,CURLOPT_SSLKEY, realpath('./pay/wxpay/apiclient_key.pem'));
    curl_setopt($ch,CURLOPT_CAINFO, realpath('./pay/wxpay/rootca.pem'));
    curl_setopt($ch,CURLOPT_POST, 1);
    curl_setopt($ch,CURLOPT_POSTFIELDS, $vars);

    $data['response'] = curl_exec($ch);
    if (curl_errno($ch)) {
        $data['error'] = curl_error($ch);
    }
    curl_close($ch);
}
