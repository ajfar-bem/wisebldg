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

$(onStart); //short-hand for $(document).ready(onStart);
function onStart($) {
    var setHeight = $("#dispp").height();
    $("#actt").height(setHeight+'px');
    $("#actt1").height(setHeight+'px');

    $("#Setpoint").slider({
        value: Setpoint,
        orientation: "horizontal",
        range: "min",
        animate: true,
        min: 0,
        max: 100,
        step: 1,
        slide: function (event, ui) {
            $("#Setpoint_val").html(ui.value);
        }
    });

    $(".slider").slider("float");

    if (role == 'tenant') {
         $('#Setpoint').slider("disable");
    }
}

$( document ).ready(function() {
    $.csrftoken();

    var _values_on_submit = {};
    var update_time;

    var ws = new WebSocket("ws://" + window.location.host +  "/socket_agent/"+device_data.agent_id);
     ws.onopen = function () {
         ws.send("WS opened from html page");
     };
     ws.onmessage = function (event) {
         var _data = event.data;
         _data = $.parseJSON(_data);
         var topic = _data['topic'];
         var sender = _data['sender'];
          // from/agent_id/device_status_response
         // from/agent_id/device_update_response
         if (topic) {
             topic = topic.split('/');
             console.log(topic);
             if (sender == device_data.agent_id && topic[0] == 'device_status_response') {
                 if ($.type( _data['message'] ) === "string"){
                     var _message = $.parseJSON(_data['message']);
                     if ($.type(_message) != "object"){
                         _message = $.parseJSON(_message)
                     }
                     change_vav_values(_message);
                 } else if ($.type( _data['message'] ) === "object"){
                     change_vav_values(_data['message']);
                 }

             }
             if (sender == device_data.agent_id && topic[0] == 'update_response') {
                 var message_upd = _data['message'];
                 var popup = false
                 if ($.type( _data['message'] ) === "string"){
                    if (message_upd.indexOf('success') > -1) {
                        popup = true
                        }
                 } else if ($.type( _data['message'] ) === "object") {
                    if (message_upd['message'].indexOf('success') > -1){
                        popup = true
                        }
                 }

                 if (popup) {
                     change_vav_values_on_submit_success(_values_on_submit);
                     $('.bottom-right').notify({
                        message: { text: 'The changes made at '+update_time+" are now updated in the device!"},
                        type: 'blackgloss',

                         fadeOut: { enabled: true, delay: 5000 }
                      }).show();
                 }
             }
         }
     };

    function change_vav_values_on_submit_success(_data) {
        $('#Setpoint').slider({ value: _data.val_setpoint });
        $("#Setpoint_val").text(_data.val_setpoint);

        $("#heat_setpoint").text(_data.heat_setpoint);

 if (_data.vav_mode == 'PositionControl') {
            $("#mode").text("PositionControl");
        } else if (_data.vav_mode == 'FlowControl') {
            $("#mode").text("FlowControl");
        } else if (_data.vav_mode == 'PowerControl') {
            $("#mode").text("PowerControl");
        }
if (_data.vav_override == 'Auto') {
            $("#mode").text("Auto");
        } else if (_data.vav_mode == 'Close') {
            $("#mode").text("Close");
        } else if (_data.vav_mode == 'Open') {
            $("#mode").text("Open");
        }else if (_data.vav_mode == 'Vnom') {
            $("#mode").text("Vnom");
        } else if (_data.vav_mode == 'Vmax') {
            $("#mode").text("Vmax");
        }else if (_data.vav_mode == 'MotStop') {
            $("#mode").text("MotStop");
        } else if (_data.vav_mode == 'Pnom') {
            $("#mode").text("Pnom");
        }else if (_data.vav_mode == 'Pmax') {
            $("#mode").text("Pmax");
        }


    }

    function change_vav_values(_data) {

        $('#Setpoint').slider({ value: _data.val_setpoint });
        $("#Setpoint_val").text(_data.val_setpoint);

        $("#heat_setpoint").text(_data.heat_setpoint);


        $("#supply_temp").text(_data.supply_temperature);
        $("#room_temp").text(_data.room_temperature);
        $("#rel_position").text(_data.rel_position);
        $("#abs_position").text(_data.abs_position);

    }

    $('.dropdown-menu li').click(function(event) {
      var $target = $( event.currentTarget );
      $target.closest( '.btn-group' )
         .find( '[data-bind="label"]' ).text( $target.text() )
            .end()
         .children( '.dropdown-toggle' ).dropdown( 'toggle' );

      return false;
    });

    $('#heatplus').click(function(e){
        e.preventDefault();
        var currentVal = parseInt($("#temp_diff").text());
        if (!isNaN(currentVal) && currentVal < 95) {
            $('#temp_diff').text(currentVal + 1);
        } else {
            $('#temp_diff').text(95);
        }
    });

    $("#heatminus").click(function(e) {
            e.preventDefault();
            var currentVal = parseInt($("#temp_diff").text());
            if (!isNaN(currentVal) && currentVal > 7) {
                $('#temp_diff').text(currentVal - 1);
            } else {
                $('#temp_diff').text(7);
            }
        });



    $("#submit_vav_data").click(function(e){
        e.preventDefault();
        update_time = new Date();
	    update_time = update_time.toLocaleTimeString();
        var temp_diff = $("#temp_diff").text();



        var Setpoint_val = $("#Setpoint_val").text();
        var val_mode = $("#mode").text();
        var override = $("#override").text();
        var values = {
            "diff_temp": parseFloat(temp_diff),

            "val_setpoint": parseInt(Setpoint_val),
            "vav_mode": val_mode,
            "vav_override": override,
        };
        values.agent_id = agent_id
        _values_on_submit = values;

        var jsonText = JSON.stringify(values);
        console.log(jsonText);
        $.ajax({
              url : '/device/_update/',
              type: 'POST',
              data: jsonText,
              dataType: 'json',
              success : function(data) {
                console.log("Data submitted");
                $('.bottom-right').notify({
                    message: { text: 'VaV settings will be updated shortly' },
                    type: 'blackgloss'
                  }).show();
              },
              error: function(data) {
                  //submit_thermostat_data(values);
                  $('.bottom-right').notify({
                        message: { text: 'Something went wrong when submitting VAV data. Please try again.' },
                        type: 'blackgloss',
                      fadeOut: { enabled: true, delay: 5000 }
                    }).show();
              }
		 });

    });

});