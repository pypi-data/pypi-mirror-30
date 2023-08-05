# coding: utf-8

"""
    Smooch

    The Smooch API is a unified interface for powering messaging in your customer experiences across every channel. Our API speeds access to new markets, reduces time to ship, eliminates complexity, and helps you build the best experiences for your customers. For more information, visit our [official documentation](https://docs.smooch.io).

    OpenAPI spec version: 3.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

import sys
import os
import re

# python 2 and python 3 compatibility library
from six import iteritems

from ..configuration import Configuration
from ..api_client import ApiClient


class ConversationApi(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    Ref: https://github.com/swagger-api/swagger-codegen
    """

    def __init__(self, api_client=None):
        config = Configuration()
        if api_client:
            self.api_client = api_client
        else:
            if not config.api_client:
                config.api_client = ApiClient()
            self.api_client = config.api_client

    def delete_messages(self, app_id, user_id, **kwargs):
        """
        Clears the message history for a user, permanently deleting all messages, but leaving any connections to Messaging Channels and Business Systems intact. These connections allow for the conversation to continue in the future, while still being associated to the same appUser. 
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.delete_messages(app_id, user_id, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str app_id: Identifies the app. (required)
        :param str user_id: Identifies the user. Can be either the smoochId or the userId. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('callback'):
            return self.delete_messages_with_http_info(app_id, user_id, **kwargs)
        else:
            (data) = self.delete_messages_with_http_info(app_id, user_id, **kwargs)
            return data

    def delete_messages_with_http_info(self, app_id, user_id, **kwargs):
        """
        Clears the message history for a user, permanently deleting all messages, but leaving any connections to Messaging Channels and Business Systems intact. These connections allow for the conversation to continue in the future, while still being associated to the same appUser. 
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.delete_messages_with_http_info(app_id, user_id, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str app_id: Identifies the app. (required)
        :param str user_id: Identifies the user. Can be either the smoochId or the userId. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['app_id', 'user_id']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_messages" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'app_id' is set
        if ('app_id' not in params) or (params['app_id'] is None):
            raise ValueError("Missing the required parameter `app_id` when calling `delete_messages`")
        # verify the required parameter 'user_id' is set
        if ('user_id' not in params) or (params['user_id'] is None):
            raise ValueError("Missing the required parameter `user_id` when calling `delete_messages`")


        collection_formats = {}

        path_params = {}
        if 'app_id' in params:
            path_params['appId'] = params['app_id']
        if 'user_id' in params:
            path_params['userId'] = params['user_id']

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.\
            select_header_content_type(['application/json'])

        # Authentication setting
        auth_settings = ['jwt']

        return self.api_client.call_api('/apps/{appId}/appusers/{userId}/messages', 'DELETE',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type=None,
                                        auth_settings=auth_settings,
                                        callback=params.get('callback'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def get_messages(self, app_id, user_id, **kwargs):
        """
        Get the specified app user's messages.
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.get_messages(app_id, user_id, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str app_id: Identifies the app. (required)
        :param str user_id: Identifies the user. Can be either the smoochId or the userId. (required)
        :param str before: Timestamp of message. The API will return 100 messages before the specified timestamp (excluding any messages with the provided timestamp).
        :param str after: Timestamp of message. The API will return 100 messages after the specified timestamp (excluding any messages with the provided timestamp).
        :return: GetMessagesResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('callback'):
            return self.get_messages_with_http_info(app_id, user_id, **kwargs)
        else:
            (data) = self.get_messages_with_http_info(app_id, user_id, **kwargs)
            return data

    def get_messages_with_http_info(self, app_id, user_id, **kwargs):
        """
        Get the specified app user's messages.
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.get_messages_with_http_info(app_id, user_id, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str app_id: Identifies the app. (required)
        :param str user_id: Identifies the user. Can be either the smoochId or the userId. (required)
        :param str before: Timestamp of message. The API will return 100 messages before the specified timestamp (excluding any messages with the provided timestamp).
        :param str after: Timestamp of message. The API will return 100 messages after the specified timestamp (excluding any messages with the provided timestamp).
        :return: GetMessagesResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['app_id', 'user_id', 'before', 'after']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_messages" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'app_id' is set
        if ('app_id' not in params) or (params['app_id'] is None):
            raise ValueError("Missing the required parameter `app_id` when calling `get_messages`")
        # verify the required parameter 'user_id' is set
        if ('user_id' not in params) or (params['user_id'] is None):
            raise ValueError("Missing the required parameter `user_id` when calling `get_messages`")


        collection_formats = {}

        path_params = {}
        if 'app_id' in params:
            path_params['appId'] = params['app_id']
        if 'user_id' in params:
            path_params['userId'] = params['user_id']

        query_params = []
        if 'before' in params:
            query_params.append(('before', params['before']))
        if 'after' in params:
            query_params.append(('after', params['after']))

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.\
            select_header_content_type(['application/json'])

        # Authentication setting
        auth_settings = ['jwt']

        return self.api_client.call_api('/apps/{appId}/appusers/{userId}/messages', 'GET',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='GetMessagesResponse',
                                        auth_settings=auth_settings,
                                        callback=params.get('callback'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def post_message(self, app_id, user_id, message_post_body, **kwargs):
        """
        Post a message to or from the app user.
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.post_message(app_id, user_id, message_post_body, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str app_id: Identifies the app. (required)
        :param str user_id: Identifies the user. Can be either the smoochId or the userId. (required)
        :param MessagePost message_post_body: Body for a postMessage request. Additional arguments are necessary based on message type ([text](https://docs.smooch.io/rest#text-message), [image](https://docs.smooch.io/rest#image-message), [carousel](https://docs.smooch.io/rest#carousel-message), [list](https://docs.smooch.io/rest#list-message))  (required)
        :return: MessageResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('callback'):
            return self.post_message_with_http_info(app_id, user_id, message_post_body, **kwargs)
        else:
            (data) = self.post_message_with_http_info(app_id, user_id, message_post_body, **kwargs)
            return data

    def post_message_with_http_info(self, app_id, user_id, message_post_body, **kwargs):
        """
        Post a message to or from the app user.
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.post_message_with_http_info(app_id, user_id, message_post_body, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str app_id: Identifies the app. (required)
        :param str user_id: Identifies the user. Can be either the smoochId or the userId. (required)
        :param MessagePost message_post_body: Body for a postMessage request. Additional arguments are necessary based on message type ([text](https://docs.smooch.io/rest#text-message), [image](https://docs.smooch.io/rest#image-message), [carousel](https://docs.smooch.io/rest#carousel-message), [list](https://docs.smooch.io/rest#list-message))  (required)
        :return: MessageResponse
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['app_id', 'user_id', 'message_post_body']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method post_message" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'app_id' is set
        if ('app_id' not in params) or (params['app_id'] is None):
            raise ValueError("Missing the required parameter `app_id` when calling `post_message`")
        # verify the required parameter 'user_id' is set
        if ('user_id' not in params) or (params['user_id'] is None):
            raise ValueError("Missing the required parameter `user_id` when calling `post_message`")
        # verify the required parameter 'message_post_body' is set
        if ('message_post_body' not in params) or (params['message_post_body'] is None):
            raise ValueError("Missing the required parameter `message_post_body` when calling `post_message`")


        collection_formats = {}

        path_params = {}
        if 'app_id' in params:
            path_params['appId'] = params['app_id']
        if 'user_id' in params:
            path_params['userId'] = params['user_id']

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'message_post_body' in params:
            body_params = params['message_post_body']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.\
            select_header_content_type(['application/json'])

        # Authentication setting
        auth_settings = ['jwt']

        return self.api_client.call_api('/apps/{appId}/appusers/{userId}/messages', 'POST',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='MessageResponse',
                                        auth_settings=auth_settings,
                                        callback=params.get('callback'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def reset_unread_count(self, app_id, user_id, **kwargs):
        """
        Reset the unread count of the conversation to 0.
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.reset_unread_count(app_id, user_id, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str app_id: Identifies the app. (required)
        :param str user_id: Identifies the user. Can be either the smoochId or the userId. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('callback'):
            return self.reset_unread_count_with_http_info(app_id, user_id, **kwargs)
        else:
            (data) = self.reset_unread_count_with_http_info(app_id, user_id, **kwargs)
            return data

    def reset_unread_count_with_http_info(self, app_id, user_id, **kwargs):
        """
        Reset the unread count of the conversation to 0.
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.reset_unread_count_with_http_info(app_id, user_id, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str app_id: Identifies the app. (required)
        :param str user_id: Identifies the user. Can be either the smoochId or the userId. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['app_id', 'user_id']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method reset_unread_count" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'app_id' is set
        if ('app_id' not in params) or (params['app_id'] is None):
            raise ValueError("Missing the required parameter `app_id` when calling `reset_unread_count`")
        # verify the required parameter 'user_id' is set
        if ('user_id' not in params) or (params['user_id'] is None):
            raise ValueError("Missing the required parameter `user_id` when calling `reset_unread_count`")


        collection_formats = {}

        path_params = {}
        if 'app_id' in params:
            path_params['appId'] = params['app_id']
        if 'user_id' in params:
            path_params['userId'] = params['user_id']

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.\
            select_header_content_type(['application/json'])

        # Authentication setting
        auth_settings = ['jwt']

        return self.api_client.call_api('/apps/{appId}/appusers/{userId}/conversation/read', 'POST',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type=None,
                                        auth_settings=auth_settings,
                                        callback=params.get('callback'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def trigger_typing_activity(self, app_id, user_id, typing_activity_trigger_body, **kwargs):
        """
        Notify Smooch when an app maker starts or stops typing a response.
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.trigger_typing_activity(app_id, user_id, typing_activity_trigger_body, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str app_id: Identifies the app. (required)
        :param str user_id: Identifies the user. Can be either the smoochId or the userId. (required)
        :param TypingActivityTrigger typing_activity_trigger_body: Body for a triggerTypingActivity request. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('callback'):
            return self.trigger_typing_activity_with_http_info(app_id, user_id, typing_activity_trigger_body, **kwargs)
        else:
            (data) = self.trigger_typing_activity_with_http_info(app_id, user_id, typing_activity_trigger_body, **kwargs)
            return data

    def trigger_typing_activity_with_http_info(self, app_id, user_id, typing_activity_trigger_body, **kwargs):
        """
        Notify Smooch when an app maker starts or stops typing a response.
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.trigger_typing_activity_with_http_info(app_id, user_id, typing_activity_trigger_body, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str app_id: Identifies the app. (required)
        :param str user_id: Identifies the user. Can be either the smoochId or the userId. (required)
        :param TypingActivityTrigger typing_activity_trigger_body: Body for a triggerTypingActivity request. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['app_id', 'user_id', 'typing_activity_trigger_body']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method trigger_typing_activity" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'app_id' is set
        if ('app_id' not in params) or (params['app_id'] is None):
            raise ValueError("Missing the required parameter `app_id` when calling `trigger_typing_activity`")
        # verify the required parameter 'user_id' is set
        if ('user_id' not in params) or (params['user_id'] is None):
            raise ValueError("Missing the required parameter `user_id` when calling `trigger_typing_activity`")
        # verify the required parameter 'typing_activity_trigger_body' is set
        if ('typing_activity_trigger_body' not in params) or (params['typing_activity_trigger_body'] is None):
            raise ValueError("Missing the required parameter `typing_activity_trigger_body` when calling `trigger_typing_activity`")


        collection_formats = {}

        path_params = {}
        if 'app_id' in params:
            path_params['appId'] = params['app_id']
        if 'user_id' in params:
            path_params['userId'] = params['user_id']

        query_params = []

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        if 'typing_activity_trigger_body' in params:
            body_params = params['typing_activity_trigger_body']
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.\
            select_header_content_type(['application/json'])

        # Authentication setting
        auth_settings = ['jwt']

        return self.api_client.call_api('/apps/{appId}/appusers/{userId}/conversation/activity', 'POST',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type=None,
                                        auth_settings=auth_settings,
                                        callback=params.get('callback'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)
