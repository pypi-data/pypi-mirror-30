All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Description: pyspreadsheet
        =====
        
        A python package to easily send data to Google Sheets
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
        
        1) Installation
        '''''''''''''''
        
        Open a terminal and install pyspreadsheet package
        
        ::
        
            pip install pyspreadsheet
        
        
        2) Use
        ''''''
        
        1) Find a client_secrets.json file
        
        Log into the Google Developers Console with the Google account whose spreadsheets you want to access. Create (or select) a project and enable the Drive API and Sheets API (under Google Apps APIs).
        Go to the Credentials for your project and create New credentials > OAuth client ID > of type Other. In the list of your OAuth 2.0 client IDs click Download JSON for the Client ID you just created. Save the file as client_secrets.json.
        
        
        2) Be sure that you have set environment variables with path to client_secrets.json file (by default ./)  and a path where pyspreadsheet will store Google Credentials (by default ./)
        
        
        ::
        
            export GOOGLE_CLIENT_SECRET_PATH="./"
            export GOOGLE_CREDENTIALS_PATH="./"
        
        3) Prepare your data like that:
        
        
        .. code:: python
        
            data = {
                    "worksheet_name"    : 'name_of_the_worsheet_you_want_to_send_data'
                    "columns_name"  : [first_column_name,second_column_name,...,last_column_name],
                    "rows"      : [[first_raw_value,second_raw_value,...,last_raw_value],...]
                }
        
        4) Send your data to the right with the sheet_id paramater:
        
        
        .. code:: python
        
            import pyspreadsheet
            pyspreadsheet.send_to_sheet(sheet_id, data)
        
        - pyspreadsheet will warn you if it has to overwrite some data, except if first row (column_name) are the same than column_name you want to send
        
        2) Import from Redshift to Google Sheets
        ''''''''''''''''''''''''''''''''''''''''
        pyspreadsheet has a function to export result of a Amazon Redshift query to a Google Sheet. This use `pyred <https://github.com/dacker-team/pyred/>`_.
        Simply write:
        
        
        .. code:: python
        
            import pyspreadsheet
            pyspreadsheet.redshift.query_to_sheet(sheet_id, worksheet_name, instance, query)
        
        
Keywords: send data google spreadsheet sheets easy
Platform: UNKNOWN
Requires-Python: >=3
