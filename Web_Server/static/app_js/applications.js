/**

Copyright (c) 2016, Virginia Tech
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
 following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the authors and should not be
interpreted as representing official policies, either expressed or implied, of the FreeBSD Project.

This material was prepared as an account of work sponsored by an agency of the United States Government. Neither the
United States Government nor the United States Department of Energy, nor Virginia Tech, nor any of their employees,
nor any jurisdiction or organization that has cooperated in the development of these materials, makes any warranty,
express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness or
any information, apparatus, product, software, or process disclosed, or represents that its use would not infringe
privately owned rights.

Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer, or
otherwise does not necessarily constitute or imply its endorsement, recommendation, favoring by the United States
Government or any agency thereof, or Virginia Tech - Advanced Research Institute. The views and opinions of authors
expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof.

VIRGINIA TECH – ADVANCED RESEARCH INSTITUTE
under Contract DE-EE0006352

#__author__ = "BEMOSS Team"
#__credits__ = ""
#__version__ = "2.0"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2016-03-14 11:23:33"

**/

$( document ).ready(function() {
    $.csrftoken();

    var ws = new WebSocket("ws://" + window.location.host + "/socket_agent/devicediscoveryagent");

     ws.onopen = function () {
         ws.send("WS opened from html page");
     };

     ws.onmessage = function (event) {
         var _data = event.data;
         if (_data == 'Open_Success'){
             return
         }
            _data = $.parseJSON(_data);
         var topic = _data['topic'];
         var sender = _data['sender'];
         var message = _data['message'];

     };

    function update_discovery_status_off(message){
        if (role == 'admin' || zone == uzone){

            $("#pnp_on").css('display','none');
            $("#pnp_off").css('display','block');
            $("#disc_selected").prop('disabled', false);

        }

    }

    function update_discovery_status_on(message){
        if (role == 'admin' || zone == uzone){
             $("#pnp_on").css('display','block');
             $("#pnp_off").css('display','none');
             $("#disc_selected").prop('disabled', false);
        }

    }

    ht = $(".eq_height_hvac").height();
    $(".eq_height_lt").height(ht);
    $(".eq_height_pl").height(ht);
    $(".eq_height_ss").height(ht);
    $(".eq_height_pm").height(ht);
    $(".eq_height_DER").height(ht);
    $(".eq_height_cam").height(ht);

    $('#iblc_add').click( function(evt){
          evt.preventDefault();
            var building = $('#drop-dr-building-select').find(":selected").val();
            var message = {'app_name':'iblc','app_data':{'building': building}};
            var jsonText = JSON.stringify(message);
            app_add(jsonText)
        });

    $('#dr_test').click( function(evt){
          evt.preventDefault();
            var building = $('#drop-dr-building-select').find(":selected").val();
            var message = {'app_name':'dr_test','app_data':{'building': building}};
            var jsonText = JSON.stringify(message);
            app_add(jsonText)
        });

    $('#fault_add').click( function(evt){
          evt.preventDefault();
          var thermostat = $('#drop-thermostats-fault').find(":selected").val();
            var building = $('#drop-dr-building-select').find(":selected").val();
            var message = {'app_name':'fault_detection','app_data':{'thermostat':thermostat,'building': building}};
            var jsonText = JSON.stringify(message);
            app_add(jsonText)
        });
    $('#thermostat_control_add').click( function(evt){
          evt.preventDefault();
          var thermostat = $('#drop-thermostats-control').find(":selected").val();
            var building = $('#drop-dr-building-select').find(":selected").val();
            var message = {'app_name':'thermostat_control','app_data':{'thermostat':thermostat,'building': building}};
            var jsonText = JSON.stringify(message);
            app_add(jsonText)
        });
    function app_add(type){
        $.ajax({
                url: '/application/app_add/',
                type: 'POST',
                data: type,
                dataType: 'json',
                success: function (data) {
                    $('.bottom-right').notify({
                        message: {text: 'Your application has been added in database.'},
                        type: 'blackgloss',
                        fadeOut: {enabled: true, delay: 5000}
                    }).show();
                     setTimeout(function(){
                     window.location.reload();
            }, 1000);
                },
                error: function (data) {
                    $('.bottom-right').notify({
                        message: {text: 'Communication Error. Try agaisn later!'},
                        type: 'blackgloss',
                        fadeOut: {enabled: true, delay: 1000}
                    }).show();
                }
            });
    }


});
