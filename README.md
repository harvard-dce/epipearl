epipearl
===============================

Python client for [epiphan-pearl][pearl]. It provides a client interface for
epiphan-pearl [http api][pearl-http-api], and some of its web ui configuration
interface, and DCE custom web ui configuration as well.

Current version of Epipearl is tested against _v3.15.3f_ firmware.

This software shoud be considered alpha, therefore likely to change/break in the near future.


install
-------

    pip install epipearl



example usage to get and set channels parameters
------------------------------------------------

    from epipearl import Epipearl
    client = Epipearl( "http://epiphan_pearl_address", "admin", "secret_password" )
    
    # to get the type of stream being published and frame size for channel 1
    response = client.get_params( channel='1', params={'publish_type':'', 'framesize':''})
    print "publish_type is %s" % response['publish_type']
    print "framsize is %s" % response['framesize']
    
    # to start recording on recorder 2
    response = client.set_params( channel='m2', params={'rec_enabled': 'on'})
    if response:
        print "recorder 2 set to start recording"



example usage of web ui methods
------------------------------------------------

Besides the HTTP API calls `get_params()` and `set_params()`, epipearl exposes
some web ui HTML form posts as python calls.

For example, if you need to create a new channel:

    # create the client
    import requests
    from epipearl.errors import SettingConfigError
    from epipearl.errors IndiscernibleResponseFromWebUiError
    from epipearl import Epipearl
    client = Epipearl( "http://epiphan_pearl_address", "admin", "secret_password" )

    # to create a channel, give it a name
    channel_id = client.create_channel('my new epiphan-pearl channel')

    # the returned channel_id is the id to be used to reference this channel
    # in all subsequent operations, like setting the rtmp-push settings
    try:
        client.set_channel_rtmp(
            channel_id=channel_id,
            rtmp_url='rtmp://some.url.where.to.push.to.eg.akamai',
            rtmp_stream='stream_name',
            rtmp_usr='user_for_rtmp_eg_akamai_account',
            rtmp_pwd='password')
    except requests.HTTPError:
        print 'error during http request'
    except SettingConfigError as e:
        print 'device web ui returned error or some settings did not take'
        print e.message
    except IndiscernibleResponseFromWebUiError:
        print 'did not understand response from device web ui'
        print e.message
    else:
        print 'channel({}) rtmp settings done'.format(channel_id)'


For examples on all implemented web ui calls, please check the unit tests in
the tests dir of a local clone. Tests also host examples of json files for
layout inputs and expected json responses from device.



testing
------------------------------------------------

During development, epipearl tests were executed using [pytest][pytest].

To run test from a local git clone:

    pip install -r requirements_dev.txt

then, to rul all tests:

    py.test tests


You can also run live tests, but these require some environment variables to be
set:

- EPI\_URL: the url to reach the epiphan-pearl web ui
- EPI\_USER: the admin username for epiphan-pearl web ui
- EPI\_PASSWD: the admin password for epiphan-pearl web ui
- EPI\_PUBLISH\_TYPE: 0 or 6 to stop or start rtmp push in epiphan-pearl

Set these in the environment and do

    export EPI_URL=http://epiphan_pearl_address
    export EPI_USER=admin_user
    export EPI_PASSWD=secret_password
    export EPI_PUBLISH_TYPE=0  # stop rtmp pushing
    py.test tests --runlive

Live tests will connect with actual device and change its settings.



license
-------

epipearl is licensed under the Apache 2.0 license



copyright
---------

2015~2016 President and Fellows of Harvard College

[cookiecutter]: https://github.com/audreyr/cookiecutter
[dce-pypackage]: https://github.com/harvard-dce/cookiecutter-dce
[pearl]: http://www.epiphan.com/products/pearl/
[pearl-http-api]:
http://31t4ggyuf393hqweo1aq90k7.wpengine.netdna-cdn.com/wp-content/uploads/2014/09/Epiphan_Pearl_userguide.pdf
[pytest]: http://pytest.org/latest/
