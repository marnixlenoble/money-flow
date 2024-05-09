firebase functions:secrets:set BUNQ_CONF
read -p 'Please type the version of the secret you just created: ' secretVersion
sed -i "/^BUNQ_CONFIG_SECRET_PERMANENT_VERSION=/s/=.*/="${secretVersion}"/" functions/bunq_money_flow/.env
