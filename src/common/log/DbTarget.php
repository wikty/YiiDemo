<?php
namespace app\common\log;

use Yii;
use yii\db\Connection;
use yii\base\InvalidConfigException;
use yii\di\Instance;
use yii\helpers\VarDumper;
use yii\log\Target;
use yii\web\Request;


class DbTarget extends Target
{
    /**
     * The database schema is:
     *   app|level|category|log_time|prefix|message
     * Database schema could be initialized by applying migration:
     *   yii migrate --migrationPath=@yii/log/migrations/
     */

    /**
     * @var Connection|array|string the DB connection object or the application component ID of the DB connection.
     * After the DbTarget object is created, if you want to change this property, you should only assign it with a DB connection object.
     * Starting from version 2.0.2, this can also be a configuration array for creating the object.
     */
    public $db = 'db';

    /**
     * @var string name of the DB table to store cache content. Defaults to "log".
     */
    public $logTable = '{{%log}}';

    /**
     * Initializes the DbTarget component.
     * This method will initialize the [[db]] property to make sure it refers to a valid DB connection.
     * @throws InvalidConfigException if [[db]] is invalid.
     */
    public function init()
    {
        parent::init();
        $this->db = Instance::ensure($this->db, Connection::className());
    }

    /**
     * Returns a string to be prefixed to the given message.
     * If [[prefix]] is configured it will return the result of the callback.
     * The default implementation will return user IP, user ID and session ID as a prefix.
     * @param array $message the message being exported.
     * The message structure follows that in [[Logger::messages]].
     * @return string the prefix string
     */
    public function getMessagePrefix($message)
    {
        if ($this->prefix !== null) {
            // call the callback [[$this->prefix]] with the parameter $message
            return call_user_func($this->prefix, $message);
        }

        if (Yii::$app === null) {
            return '';
        }

        $request = Yii::$app->getRequest();
        $ip = $request instanceof Request ? $request->getUserIP() : '-';

        /* @var $user \yii\web\User */
        $user = Yii::$app->has('user', true) ? Yii::$app->get('user') : null;
        if ($user && ($identity = $user->getIdentity(false))) {
            $userID = $identity->getId();
        } else {
            $userID = '-';
        }

        /* @var $session \yii\web\Session */
        $session = Yii::$app->has('session', true) ? Yii::$app->get('session') : null;
        $sessionID = $session && $session->getIsActive() ? $session->getId() : '-';

        return "[$ip][$userID][$sessionID]";
    }

    /**
     * Stores log messages to DB.
     */
    public function export()
    {
        $tableName = $this->db->quoteTableName($this->logTable);
        $sql = "INSERT INTO $tableName ([[app]], [[level]], [[category]], [[log_time]], [[prefix]], [[message]])
                VALUES (:app, :level, :category, :log_time, :prefix, :message)";
        $command = $this->db->createCommand($sql);
        foreach ($this->messages as $message)
        {
            list($text, $level, $category, $timestamp) = $message;
            if (!is_string($text))
            {
                $text = VarDumper::export($text);
            }
            $command->bindValues([
                ':app' => Yii::$app->id,
                ':level' => $level,
                ':category' => $category,
                ':log_time' => $timestamp,
                ':prefix' => $this->getMessagePrefix($message),
                ':message' => $text,
            ])->execute();
        }
    }
}
