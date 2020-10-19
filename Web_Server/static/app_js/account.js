/**
 * Created by cmmoo on 8/24/17.
 */
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

#__author__ = "Mengmeng Cai"
#__credits__ = ""
#__version__ = "2.0"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2017-08-24 12:04:50"
#__lastUpdated__ = "2017-08-24 11:23:33"

**/

$( document ).ready(function() {

    $.csrftoken();

    $('.widget-content').on('click', '#add_new_building', function(e) {
        e.preventDefault();

        var table =$('#tb_buildings').children()[1];
        console.log(table);


        var tr_id = $('#tb_buildings tbody tr:last').attr('id');
        console.log( tr_id);
        if (tr_id==undefined)
        {
        tr_id="bd_0";
        }
        tr_id = tr_id.split("_");
        tr_id = tr_id[1];

        if (tr_id == '') {
            tr_id = 0;
        }
        var new_tr_id = parseInt(tr_id) + 1 ;

        var row = table.insertRow();
        row.id = "bd_" + new_tr_id;

		var cell1 = row.insertCell(0);
        var cell2 = row.insertCell(1);
        cell1.className = 'col-sm-4';
        cell2.className = 'col-sm-2';

		cell1.innerHTML = "<td class='col-md-4'><input type='text' placeholder='' id='bdname_"+new_tr_id+"' class='form-control' name='buildinglist' value=''></td>";

        cell2.innerHTML = "<button class='btn btn-sm btn-danger delete_td' type='button' id='delete_" + new_tr_id + "'>X</button>";



    });

    $('.widget-content').on('click', "button[id^='delete_']" , function(e) {
    e.preventDefault();

    var tp_id = this.id;
    tp_id = tp_id.split("_");
    var delete_id = tp_id[1];
    $("#bd_" + delete_id).remove();

    });



});
