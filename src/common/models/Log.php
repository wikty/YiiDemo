<?php

namespace app\models;

use Yii;

/**
 * This is the model class for table "log".
 *
 * @property string $app
 * @property string $level
 * @property string $category
 * @property int $log_time
 * @property string $prefix
 * @property string $message
 */
class Log extends \yii\db\ActiveRecord
{
    /**
     * {@inheritdoc}
     */
    public static function tableName()
    {
        return 'log';
    }

    /**
     * {@inheritdoc}
     */
    public function rules()
    {
        return [
            [['app', 'level', 'category', 'log_time', 'prefix', 'message'], 'required'],
            [['app', 'level', 'category', 'prefix', 'message'], 'string'],
            [['log_time'], 'integer'],
        ];
    }

    /**
     * {@inheritdoc}
     */
    public function attributeLabels()
    {
        return [
            'app' => 'App',
            'level' => 'Level',
            'category' => 'Category',
            'log_time' => 'Log Time',
            'prefix' => 'Prefix',
            'message' => 'Message',
        ];
    }
}
