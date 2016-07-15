#!/bin/bash

set -e
HEADERS="-H 'Content-Type: application/json'"
CURL="curl -k "
API_URL_PRE="https://qyapi.weixin.qq.com/cgi-bin/"
CF=
token=
token_timeout=0
SOURCE="${0}"
SCRIPTDIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

# Print error message and exit with error
_exiterr() 
{
    echo "ERROR: ${1}" >&2
    exit 1
}

check_cf()
{
  for cf in "$1" "$SCRIPTDIR/weixin-corp.ini" /etc/weixin-corp.ini /tmp/weixin-corp.ini ; do
      [[ "x$cf" != "x" ]] && test -f $cf && CF=${cf} && break
  done

  test -f "${CF}"  || _exiterr "cf file not exist, cf file must like this: arg1 | /etc/weixin-corp.ini | /tmp/weixin-corp.ini"
  test -w "${CF}"  || _exiterr "cf file no wirte permission!"
  test -f "${CF}" && . "${CF}"
  [[ "x" == "x$CORP_ID" ]] && _exiterr "Bad cf format, must shell formart(ini) CORP_ID=?? not found."
  [[ "x" == "x$CORP_SEC" ]] && _exiterr "Bad cf format, must shell formart(ini) CORP_SEC=?? not found."
  echo a >/dev/null
}

check_deps()
{
    echo abc | grep -q a > /dev/null 2>&1 || _exiterr "This script requires grep."
    mktemp -u -t XXXXXX > /dev/null 2>&1 || _exiterr "This script requires mktemp."
    sed "" < /dev/null > /dev/null 2>&1 || _exiterr "This script requires sed"
    $CURL -V > /dev/null 2>&1 || _exiterr "This script requires curl"
}

# Get string value from json dictionary
get_json_string_value() 
{
    printf '%s\n' "${1}" |
    grep -Eo '"'"${2}"'":[[:space:]]*"[^"]*"' | cut -d'"' -f4
}
get_json_int_value()
{
    printf '%s\n' "${1}" |
    grep -Eo '"'"${2}"'":[[:space:]]*[0-9]+' | grep -Eo '[0-9]+$'
}

# Send http(s) request with specified method by curl
http_request() 
{
    tempcont="$(mktemp -t XXXXXX)"
    set +e
    if [[ "${1}" = "head" ]]; then
        statuscode="$($CURL -s -w "%{http_code}" -o "${tempcont}" "${2}" -I)"
        curlret="${?}"
    elif [[ "${1}" = "get" ]]; then
        statuscode="$($CURL -s -w "%{http_code}" -o "${tempcont}" "${2}")"
        curlret="${?}"
    elif [[ "${1}" = "post" ]]; then
        statuscode="$($CURL-s -w "%{http_code}" "$HEADERS" -o "${tempcont}" "${2}" -d "${3}")"
        curlret="${?}"
    else
        set -e
        rm -f "${tempcont}"
        _exiterr "Unknown request method: ${1}"
    fi
    set -e
    if [[ ${curlret} -ne 0 ]]; then
        rm -f "${tempcont}"
        _exiterr "Problem connecting to server (curl returned with ${curlret})"
    fi

    if [[ ! "${statuscode:0:1}" = "2" ]]; then
        echo "  + ERROR: An error occurred while sending ${1}-request to ${2} (Status ${statuscode})" >&2
        echo >&2
        echo "Details:" >&2
        cat "${tempcont}" >&2
        rm -f "${tempcont}"
    fi
    cat "${tempcont}"
    rm -f "${tempcont}"
}

save_token()
{
    token=$1
    timeout=$2
    
    sed -i '/^token=/d' "$CF"
    sed -i '/^token_timeout=/d' "$CF"
    echo "token=$token" >> "$CF"
    echo "token_timeout=$timeout" >> "$CF"
}

get_token()
{
    now=$(date +%s)
    if [[ $now -lt $token_timeout ]]; then
        echo $token
        return 0
    else
        echo "Token expired, get new from weixin api server."
        url_last="gettoken?corpid=${CORP_ID}&corpsecret=${CORP_SEC}"
        rsp=$(http_request get "${API_URL_PRE}${url_last}")
        echo "$rsp"
        token=$(get_json_string_value "$rsp"  access_token)
        token_exp=$(get_json_int_value "$rsp"  expires_in)
        [[ "x$token" == "x" ]] && _exiterr "Cannot get access_token from weixin api."
        [[ "x$token_exp" == "x" ]] &&  token_exp=7200
        let token_timeout=$now+$token_exp-10
        save_token "$token" "$token_timeout"
        echo $token
    fi
}

wx_request()
{
    cgi=$1
    
    get_token
    url="${API_URL_PRE}${cgi}?access_token=${token}"
    http_request post "${url}" "$2"
}

send_text()
{
    aid=$3
    [[ "x" == "x$aid" ]] && aid=2
    data='{"touser":"'"${1}"'","msgtype": "text","agentid":'${aid}',"text": {"content":"'"$2"'"},"safe":"0"}'
    wx_request "message/send" "$data"
}
check_deps
check_cf
send_text yangyou "$1"
