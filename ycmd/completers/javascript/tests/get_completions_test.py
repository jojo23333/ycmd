#
# Copyright (C) 2015  ycmd contributors
#
# This file is part of YouCompleteMe.
#
# YouCompleteMe is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# YouCompleteMe is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with YouCompleteMe.  If not, see <http://www.gnu.org/licenses/>.

from ycmd.server_utils import SetUpPythonPath
SetUpPythonPath()

import bottle, httplib, os, time

from nose.tools import with_setup
from hamcrest import ( contains,
                       contains_inanyorder,
                       empty,
                       has_entries )

from ycmd.tests.test_utils import ( BuildRequest, Setup )
from ycmd.tests.get_completions_test import ( CompletionEntryMatcher,
                                              GetCompletions_RunTest )

bottle.debug( True )


def PathToTestFile( *args ):
  return os.path.join( os.path.dirname( __file__ ), 'testdata', *args )


def WaitForTernServerReady( app ):
  app.post_json( '/run_completer_command', BuildRequest(
    command_arguments = [ 'StartServer' ],
    completer_target = 'filetype_default',
    filetype = 'javascript',
    filepath = '/foo.js',
    contents = '',
    line_num = '1'
  ) )

  retries = 100
  while retries > 0:
    result = app.get( '/ready', { 'subserver': 'javascript' } ).json
    if result:
      return

    time.sleep( 0.2 )
    retries = retries - 1

  raise RuntimeError( 'Timeout waiting for Tern.js server to be ready' )


@with_setup( Setup )
def GetCompletions_TernCompleter_Works_NoQuery_test():
  GetCompletions_RunTest( {
    'description': 'semantic completion works for simple object no query',
    'request': {
      'filetype':   'javascript',
      'filepath':   PathToTestFile( 'simple_test.js' ),
      'line_num':   13,
      'column_num': 43,
    },
    'expect': {
      'response': httplib.OK,
      'data': has_entries( {
        'completions': contains_inanyorder(
          CompletionEntryMatcher( 'a_simple_function',
                                  'fn(param: ?) -> string' ),
          CompletionEntryMatcher( 'basic_type', 'number' ),
          CompletionEntryMatcher( 'object', 'object' ),
        ),
        'errors': empty(),
      } )
    },
  }, WaitForTernServerReady )


@with_setup( Setup )
def GetCompletions_TernCompleter_Works_Query_test():
  GetCompletions_RunTest( {
    'description': 'semantic completion works for simple object with query',
    'request': {
      'filetype':   'javascript',
      'filepath':   PathToTestFile( 'simple_test.js' ),
      'line_num':   14,
      'column_num': 45,
    },
    'expect': {
      'response': httplib.OK,
      'data': has_entries( {
        'completions': contains(
          CompletionEntryMatcher( 'basic_type', 'number' ),
        ),
        'errors': empty(),
      } )
    },
  }, WaitForTernServerReady )


@with_setup( Setup )
def GetCompletions_TernCompleter_Works_Require_NoQuery_test():
  GetCompletions_RunTest( {
    'description': 'semantic completion works for simple object no query',
    'request': {
      'filetype':   'javascript',
      'filepath':   PathToTestFile( 'requirejs_test.js' ),
      'line_num':   2,
      'column_num': 15,
    },
    'expect': {
      'response': httplib.OK,
      'data': has_entries( {
        'completions': contains_inanyorder(
          CompletionEntryMatcher( 'mine_bitcoin', 'fn(how_much: ?) -> number' ),
        ),
        'errors': empty(),
      } )
    },
  }, WaitForTernServerReady )


@with_setup( Setup )
def GetCompletions_TernCompleter_Works_Require_Query_test():
  GetCompletions_RunTest( {
    'description': 'semantic completion works for simple object with query',
    'request': {
      'filetype':   'javascript',
      'filepath':   PathToTestFile( 'requirejs_test.js' ),
      'line_num':   4,
      'column_num': 17,
    },
    'expect': {
      'response': httplib.OK,
      'data': has_entries( {
        'completions': contains(
          CompletionEntryMatcher( 'mine_bitcoin', 'fn(how_much: ?) -> number' ),
        ),
        'errors': empty(),
      } )
    },
  }, WaitForTernServerReady )
