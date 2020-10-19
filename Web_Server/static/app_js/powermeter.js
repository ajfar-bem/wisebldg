/**

 *  Authors: Kruthika Rathinavel
 *  Version: 2.0
 *  Email: kruthika@vt.edu
 *  Created: "2014-10-13 18:45:40"
 *  Updated: "2015-02-13 15:06:41"


 * Copyright © 2014 by Virginia Polytechnic Institute and State University
 * All rights reserved

 * Virginia Polytechnic Institute and State University (Virginia Tech) owns the copyright for the BEMOSS software and its
 * associated documentation ("Software") and retains rights to grant research rights under patents related to
 * the BEMOSS software to other academic institutions or non-profit research institutions.
 * You should carefully read the following terms and conditions before using this software.
 * Your use of this Software indicates your acceptance of this license agreement and all terms and conditions.

 * You are hereby licensed to use the Software for Non-Commercial Purpose only.  Non-Commercial Purpose means the
 * use of the Software solely for research.  Non-Commercial Purpose excludes, without limitation, any use of
 * the Software, as part of, or in any way in connection with a product or service which is sold, offered for sale,
 * licensed, leased, loaned, or rented.  Permission to use, copy, modify, and distribute this compilation
 * for Non-Commercial Purpose to other academic institutions or non-profit research institutions is hereby granted
 * without fee, subject to the following terms of this license.

 * Commercial Use: If you desire to use the software for profit-making or commercial purposes,
 * you agree to negotiate in good faith a license with Virginia Tech prior to such profit-making or commercial use.
 * Virginia Tech shall have no obligation to grant such license to you, and may grant exclusive or non-exclusive
 * licenses to others. You may contact the following by email to discuss commercial use:: vtippatents@vtip.org

 * Limitation of Liability: IN NO EVENT WILL VIRGINIA TECH, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR REDISTRIBUTE
 * THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR
 * CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO
 * LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR A FAILURE
 * OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF VIRGINIA TECH OR OTHER PARTY HAS BEEN ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGES.

 * For full terms and conditions, please visit https://bitbucket.org/bemoss/bemoss_os.

 * Address all correspondence regarding this license to Virginia Tech's electronic mail address:: vtippatents@vtip.org

**/

/**
 * @author kruthika
 */

    //var setHeight = $("#power_con").height();
    //$("#enrgy_con").height(setHeight+'px');


$( document ).ready(function() {
	$.csrftoken();


     var ws = new WebSocket("ws://" + window.location.host +  "/socket_agent/"+device_data.agent_id);

     ws.onopen = function () {
         ws.send("WS opened from html page");
     };

     ws.onmessage = function (event) {
         var _data = event.data;
         _data = $.parseJSON(_data);
         var topic = _data['topic'];          var sender = _data['sender'];
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
                     change_powermeter_values(_message);
                 } else if ($.type( _data['message'] ) === "object"){
                     change_powermeter_values(_data['message']);
                 }

             }
         }
     };

    $("#vmore").click(function (evt) {
        evt.preventDefault();
        $("#view_more").css("display", "block");
        $(this).css("display", "none");
        $("#vless").css("display", "block");
    });

    $("#vless").click(function (evt) {
        evt.preventDefault();
        $("#view_more").css("display", "none");
        $(this).css("display", "none");
        $("#vmore").css("display", "block");
    });

    (function get_powermeter_data(){
	values = {
		    "device_info": device_info
		    };
	var jsonText = JSON.stringify(values);
	setTimeout(function()
	{
		$.ajax({
		  url : '/pmstat/',
		  type: 'POST',
		  data: jsonText,
		  dataType: 'json',
		  success : function(data) {
		  	//change_tstat_values(data);
		  	get_powermeter_data();
		  },
		  error: function(data) {
			get_powermeter_data();
		  }
		 });
	},60000);
	})();

	function change_powermeter_values(data) {

        if (data.power) {
            $("#power_sum").text(data.power);
        }
        if (data.power_a) {
            $("#power_a").text(data.power_a);
        }
        if (data.power_b) {
            $("#power_b").text(data.power_b);
        }
        if (data.power_c) {
            $("#power_c").text(data.power_c);
        }

        if (data.voltage) {
            $("#voltage_avg").text(data.voltage);
        }
        if (data.voltage_a) {
            $("#voltage_a").text(data.voltage_a);
        }
        if (data.voltage_b) {
            $("#voltage_b").text(data.voltage_b);
        }
        if (data.voltage_c) {
            $("#voltage_c").text(data.voltage_c);
        }

        if (data.frequency) {
            $("#freq").text(data.frequency);
        }

        if (data.current_a) {
            $("#current_a").text(data.current_a);
        }
        if (data.current_b) {
            $("#current_b").text(data.current_b);
        }
        if (data.current_c) {
            $("#current_c").text(data.current_c);
        }

        if (data.powerfactor) {
            $("#pf_avg").text(data.powerfactor);
        }
        if (data.powerfactor_a) {
            $("#pf_a").text(data.powerfactor_a);
        }
        if (data.powerfactor_b) {
            $("#pf_b").text(data.powerfactor_b);
        }
        if (data.powerfactor_c) {
            $("#pf_c").text(data.powerfactor_c);
        }

        if (data.power_apparent_sum) {
            $("#pa_sum").text(data.power_apparent_sum);
        }
        if (data.power_apparent_a) {
            $("#pa_a").text(data.power_apparent_a);
        }
        if (data.power_apparent_b) {
            $("#pa_b").text(data.power_apparent_b);
        }
        if (data.power_apparent_c) {
            $("#pa_c").text(data.power_apparent_c);
        }

        if (data.power_reactive_sum) {
            $("#pr_sum").text(data.power_reactive_sum);
        }
        if (data.power_reactive_a) {
            $("#pr_a").text(data.power_reactive_a);
        }
        if (data.power_reactive_b) {
            $("#pr_b").text(data.power_reactive_b);
        }
        if (data.power_reactive_c) {
            $("#pr_c").text(data.power_reactive_c);
        }

        if (data.energy_apparent_sum) {
            $("#ea_sum").text(data.energy_apparent_sum);
        }
        if (data.energy_apparent_a) {
            $("#ea_a").text(data.energy_apparent_a);
        }
        if (data.energy_apparent_b) {
            $("#ea_b").text(data.energy_apparent_b);
        }
        if (data.energy_apparent_c) {
            $("#ea_c").text(data.energy_apparent_c);
        }

        if (data.energy_reactive_sum) {
            $("#er_sum").text(data.energy_reactive_sum);
        }
        if (data.energy_reactive_a) {
            $("#er_a").text(data.energy_reactive_a);
        }
        if (data.energy_reactive_b) {
            $("#er_b").text(data.energy_reactive_b);
        }
        if (data.energy_reactive_c) {
            $("#er_c").text(data.energy_reactive_c);
        }

        if (data.energy_sum) {
            $("#e_sum").text(data.energy_sum);
        }
        if (data.energy_sum_nr) {
            $("#e_sum_nr").text(data.energy_sum_nr);
        }
        if (data.energy_a_net) {
            $("#e_a").text(data.energy_a_net);
        }
        if (data.energy_b_net) {
            $("#e_b").text(data.energy_b_net);
        }
        if (data.energy_c_net) {
            $("#e_c").text(data.energy_c_net);
        }

        if (data.energy_pos_sum) {
            $("#e_pos_sum").text(data.energy_pos_sum);
        }
        if (data.energy_pos_sum_nr) {
            $("#e_pos_sum_nr").text(data.energy_pos_sum_nr);
        }
        if (data.energy_pos_a) {
            $("#e_pos_a").text(data.energy_pos_a);
        }
        if (data.energy_pos_b) {
            $("#e_pos_b").text(data.energy_pos_b);
        }
        if (data.energy_pos_c) {
            $("#e_pos_c").text(data.energy_pos_c);
        }

        if (data.energy_neg_sum) {
            $("#e_neg_sum").text(data.energy_neg_sum);
        }
        if (data.energy_neg_sum_nr) {
            $("#e_neg_sum_nr").text(data.energy_neg_sum_nr);
        }
        if (data.energy_neg_a) {
            $("#e_neg_a").text(data.energy_neg_a);
        }
        if (data.energy_neg_b) {
            $("#e_neg_b").text(data.energy_neg_b);
        }
        if (data.energy_neg_c) {
            $("#e_neg_c").text(data.energy_neg_c);
        }


    }

});