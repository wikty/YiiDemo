<?php

namespace app\common\controllers;

use Yii;
use yii\web\Controller;
use app\common\ConstCode;


class BaseApiController extends Controller {
    
    protected $params;  // to hold request arguments

    public function beforeAction($action) {
        $ok = parent::beforeAction($action);

        foreach ($_REQUEST as $key => $value) {
            $this->params[$key] = $value;
        }

        //header("Access-Control-Allow-Origin: *");

        return $ok;
    }

    public function setParam($key, $value) {
        return $this->params[$key] = $value;
    }

    public function getParam($key, $type = null) {
        if(isset($this->params[$key])) {
            switch ($type) {
                case 'i':
                case 'int':
                    return intval($this->params[$key]);
                
                case 'f':
                case 'float':
                    return floatval($this->params[$key]);

                case 's':
                case 'string':
                default:
                    return $this->params[$key];
            }
        }
        return null;
    }

    public function checkParams($requiredParams) {
        if(is_array($requiredParams)) {
            foreach($requiredParams as $param) {
                if(!isset($_REQUEST[$param])) {
                    $code = ConstCode::ERROR_PARAM_NOT_SET;
                    $message = 'param '.$param.' not set';
                    $this->finishError($message, $code);  // will die
                }
            }
        }
    }

    public function finish($response) {
        header('Content-type:application/json;charset=UTF-8');
        die(json_encode($response));  // response json data and die
    }   

    public function finishSuccess($data = null) {
        $response['code'] = ConstCode::ERROR_OK;
        $response['data'] = is_null($data) ? [] : $data;

        $this->finish($response);
    }

    public function finishError($message, $code = null, $extra = []) {
        $response['code'] = is_null($code) ? ConstCode::ERROR_UNKNOWN : intval($code);
        $data['message'] = $message;
        if(is_array($extra)) {
            $data = array_merge($data, $extra);
        }
        $response['data'] = $data;
        
        $this->finish($response);
    }
}