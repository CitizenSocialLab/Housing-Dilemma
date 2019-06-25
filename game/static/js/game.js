


function Game() {
}

Game.prototype = {

    update_cur_time: function(time) {
        this.curtime_ronda = time;
        var invtpc = this.curtime_ronda / this.dur_round;
        var tpc = (1 - invtpc);

        //ToDo: colors del timer
        if (invtpc > 0.66) {
            c3 = [0xab, 0xd9, 0xe3, 1];
        } else if (invtpc > 0.33) {
            c3 = [0xab, 0xd9, 0xe3, 1];
        } else {
            c3 = [0xab, 0xd9, 0xe3, 1];
        }

        $('#timer_progress')
            .css('width', (tpc * 100) + '%')
            .css('background-color', 'rgba(' + c3.join(',') + ')');
    },

    load_game: function(user_id, lang) {
        this.user_id = user_id;
        this.lang = lang;
    },

    start_game: function(data) {
        console.log(data)

        // Times
        this.countdown_time = data.countdown_initial_time;
        this.timer_value = 100;
        this.time_wait = data.time_wait;

        // Game, Round and Player info
        this.current_round = data.round_number;
        this.endowment_current = parseFloat(data.initial_endowment).toFixed(2);
        this.num_player = data.num_player;
        this.num_rondes = data.total_rounds;
        this.control_intervention = data.control_intervention;

        // Vars
        this.municipi = data.municipi;
        this.limit_high = parseFloat(data.limit_high).toFixed(0);
        this.limit_low = parseFloat(data.limit_low).toFixed(0);
        this.subsidy = parseFloat(data.subsidy).toFixed(2);
        this.dur_round = data.time_round;
        this.price_current = parseFloat(data.price).toFixed(0);

        this.resposta = false;

        $('#countdown_time').html(Math.ceil(this.countdown_time / 1000));
        $('#countdown-modal').modal({ backdrop: 'static', keyboard: true }).modal('show');

        var message_player = countdown_text_player;
        message_player = message_player.replace('{player}', this.num_player);
        message_player = message_player.replace('{rent}', this.endowment_current);
        message_player = message_player.replace('{municipi}', this.municipi);
        $("#countdown_text_player").html(message_player);

        var message_house = countdown_text_house;
        message_house = message_house.replace('{price}', this.price_current);
        message_house = message_house.replace('{municipi}', this.municipi);
        $("#countdown_text_house").html(message_house);

        var message_limit = '';

        if (this.control_intervention == "BOTH"){
            message_limit = countdown_text_limit + ' <br> 1.' + countdown_text_high_limit + ' <br> 2.' + countdown_text_low_limit
            message_limit = message_limit.replace('{limit_high}', this.limit_high);
            message_limit = message_limit.replace('{limit_low}', this.limit_low);
            message_limit = message_limit.replace('{subsidy}', this.subsidy);
        }
        if (this.control_intervention == "HIGH"){
            message_limit = countdown_text_limit + ' <br> 1.' + countdown_text_high_limit
            message_limit = message_limit.replace('{limit_high}', this.limit_high);
        }
        if (this.control_intervention == "LOW"){
            message_limit = countdown_text_limit + ' <br> 1.' + countdown_text_low_limit
            message_limit = message_limit.replace('{limit_low}', this.limit_low);
            message_limit = message_limit.replace('{subsidy}', this.subsidy);
        }
        if (this.control_intervention == "NONE"){}

        $("#countdown_text_limit").html(message_limit);
        $("#countdown_text_reward").html(countdown_text_reward);

        $("#countdown_text_player").show();
        $("#countdown_text_house").show();
        $("#countdown_text_limit").show();
        $("#countdown_text_reward").show();

        $("#countdown_titol").show();
        $("#countdown_time").show();

        //Setup timer and bind events
        var self = this;
        this.timer_ronda = new TimerInterval(
            function() {
                // This functions is launched in case of arrive at the end round
                // Therefore we call final results
                if(!game.resposta)
                    game.demanar_resultat();
            },
            this.dur_round,
            function(time) {  self.update_cur_time(time) },
            this.timer_value
        );


        var mytimer = this.countdown_time % 1000;
        this.countdown_time = this.countdown_time - mytimer;
        setTimeout(function(){game.countdown_inici()}, mytimer);
    },

    countdown_inici: function() {
        if (this.countdown_time>0) {
            $('#countdown_time').html(this.countdown_time / 1000);
            this.countdown_time = this.countdown_time - 1000;
            setTimeout(function(){ game.countdown_inici() }, 1000);
        } else {
            $("#countdown-modal").modal('hide');
            game.start_next_round();
        }
    },

    start_next_round: function() {
        console.log('---------------')
        console.log("Start round: " + this.current_round);

        this.resposta = false;
        this.timer_ronda.start_timer();

        text_bucket_complete =  text_bucket.replace("{savings}","<span class='bold-text-bucket'>"+ this.endowment_current +"</span>")
        $('#text-bucket').html(text_bucket_complete);

        text_contribution_complete = text_contribution.replace("{price}","<span class='bold-text-bucket'>"+ this.price_current +"</span>")
        $('#text-contribucio').html(text_contribution_complete);

        text_round_complete = text_round.replace("{round}", this.current_round)
        text_round_complete = text_round_complete.replace("{total_round}",this.num_rondes)
        $('#text-ronda').html(text_round_complete);

        if (this.round_increment == 0 && this.round_rented == 0){
            new_text_info_low_limit = text_info_low_limit.replace("{subsidy}", this.subsidy);
            new_text_info_low_limit = new_text_info_low_limit.replace("{tax}", this.tax);
            $('#text-info-extra').html(new_text_info_low_limit);
            $('#text-info-extra').show();
        }else{
            $('#text-info-extra').html();
            $('#text-info-extra').hide();
        }

        if (this.house_rented) {
            $("#button-0").hide();
            $("#button-1").hide();
            $("#text-bucket").hide();
            $("#text-contribucio").hide();
            $('#text-info-extra').hide();

            $("#waiting_main").show();
            $("#waiting_text").show();

            // If the house is rented we wait the results of the others
            game.resposta = true;
            game.demanar_resultat();
        }

        // Limitation to new number of rounds
        console.log(this.current_round);
        if (this.current_round >= 13) {
            console.log('Final modal');
            console.log('-----------');
            $('#final-modal').modal({ backdrop: 'static', keyboard: true }).modal('show');
        }
    },

    end_round:function(data) {
        console.log('---------');
        console.log('End round');
        console.log(data);
        //Si estava esperant amagar el dialeg
        $("#esperar-modal").modal('hide');     // dismiss the dialog

        this.next_round_time = data.temps_restant * 1000;
        this.current_round = data.numero_ronda;
        this.endowment_current = data.diners_inici_ronda;

        this.house_rented = data.house_rented;

        this.price_current = parseFloat(data.price_final).toFixed(2);

        this.current_player_id = data.current_player.id_user;
        this.current_player_house = data.current_player.house;


        // Players
        this.players_player_id = data.players.player_id;
        this.players_player_num = data.players.player_num;
        this.players_selection = data.players.selection;
        this.players_selection_done = data.players.selection_done;
        this.players_house = data.players.house;
        this.players_selection_order = data.players.selection_order;

        // Houses
        this.houses_player_id = data.houses.player_id;
        this.houses_player_num = data.houses.player_num;
        this.houses_rounds = data.houses.rounds;
        this.houses_price = data.houses.price;

        // Round
        this.round_round_num =  data.current_round.round_num;
        this.round_rented =  data.current_round.rented;
        this.round_player_id = data.current_round.player_id;
        this.round_player_num = data.current_round.player_num;
        this.round_price_rented = parseFloat(data.current_round.price_rented).toFixed(2);
        this.round_price_market = parseFloat(data.current_round.price_market).toFixed(2);
        this.round_price_accepted = data.current_round.price_accepted;
        this.round_price_final = parseFloat(data.price_final).toFixed(2);
        this.round_price_initial = parseFloat(data.price_initial).toFixed(2);
        this.round_increment = data.current_round.increment.toFixed(2);

        // Vars
        this.tax = data.tax;
        this.increment = parseFloat(data.increment).toFixed(0);
        //this.subsidy = data.subsidy;
        //this.limit_high = data.limit_high;
        //this.limit_low = data.limit_low;

        $('#ronda_imatge_refors').hide();
        $('#ronda_taula_resultats').show();

        if (!data.playing || this.current_round>=13) {
            //Fem que el jocs'acabi en aquest torn
            console.log('Final-modal-01')
            $('#final-modal').modal({ backdrop: 'static', keyboard: true }).modal('show');
            return;
        }

        $('#ronda-modal').modal({backdrop: 'static', keyboard: true}).modal('show');

        //Engegar timer
        $('#nextround_time').html(Math.ceil(this.next_round_time / 1000));

        this.next_round_time = this.next_round_time - 1000;
        setTimeout(function () { game.countdown_next_round() }, 1000);

        $('#modal_ronda_msg').html(text_num_ronda + ' ' + (this.current_round - 1));

        // Players
        for(index=0; index < this.players_player_num.length ; index++) {
            // is_robot
            if (this.players_selection_done[index]) robot = '';
            else robot = '*';

            text_selection = '';
            if (this.players_selection[index] == 1) {
                text_selection = text_rent;
            }else{
                text_selection = text_no_rent;
            }

            document.getElementsByClassName('text_price')[index].innerHTML = text_selection+robot;
            document.getElementsByClassName('text_player')[index].innerHTML = text_player + " " + this.players_player_num[index];
            document.getElementsByClassName('text_time')[index].innerHTML = "("+parseInt(this.players_selection_order[index]+1).toString()+"º)";


            // Hidden the players that get a house
            if (this.players_house[index]) {
                document.getElementsByClassName('text_price')[index].style.visibility = 'hidden';
                //document.getElementsByClassName('text_player')[index].style.visibility = 'hidden';
                document.getElementsByClassName('text_time')[index].style.visibility = 'hidden';
                //document.getElementsByClassName('image_player')[index].style.visibility = 'hidden';
            }

            // Show the information of player that rent the house in this round
            if (this.players_player_id[index] == this.round_player_id){

                document.getElementsByClassName('text_price')[index].style.visibility = 'visible';
                document.getElementsByClassName('text_player')[index].style.visibility = 'visible';
                document.getElementsByClassName('text_time')[index].style.visibility = 'visible';
                document.getElementsByClassName('image_player')[index].style.visibility = 'visible';

                document.getElementsByClassName('text_price')[index].style.color = "black";
                document.getElementsByClassName('text_player')[index].style.color = "black";
                document.getElementsByClassName('text_time')[index].style.color = "black";

                document.getElementsByClassName('text_price')[index].style.opacity = 1;
                document.getElementsByClassName('text_player')[index].style.opacity = 1;
                document.getElementsByClassName('text_time')[index].style.opacity = 1;

                document.getElementsByClassName('image_player')[index].style.opacity = 1;

            }else{

                document.getElementsByClassName('text_price')[index].style.color = "black";
                document.getElementsByClassName('text_player')[index].style.color = "black";
                document.getElementsByClassName('text_time')[index].style.color = "black";

                document.getElementsByClassName('text_price')[index].style.opacity = 0.5;
                document.getElementsByClassName('text_player')[index].style.opacity = 0.5;
                document.getElementsByClassName('text_time')[index].style.opacity = 0.5;

                document.getElementsByClassName('image_player')[index].style.opacity = 0.5;
            }

            // Change the color of current user
            if (this.current_player_id == this.players_player_id[index]) {
                document.getElementsByClassName('text_price')[index].style.color = "black";
                document.getElementsByClassName('text_player')[index].style.color = "black";
                document.getElementsByClassName('text_time')[index].style.color = "black";

                document.getElementsByClassName('text_price')[index].style.opacity = 1;
                document.getElementsByClassName('text_player')[index].style.opacity = 1;
                document.getElementsByClassName('text_time')[index].style.opacity = 1;

                document.getElementsByClassName('image_player')[index].style.opacity = 1;

                document.getElementsByClassName('text_player')[index].style.textDecoration = 'underline';
                document.getElementsByClassName('rectangle-player')[index].style.visibility = 'visible';
            }
        }

        // Houses
        for(index=0; index < this.houses_player_num.length; index++) {
            document.getElementsByClassName('text_price')[parseInt(this.houses_player_num[index]) - 1 + 6].innerHTML = parseFloat(this.houses_price[index]).toFixed(2) + "€";
            document.getElementsByClassName('text_round')[parseInt(this.houses_player_num[index]) - 1].innerHTML = text_month + ' ' + this.houses_rounds[index];

            // Change the color of current user
            if (this.current_player_id == this.houses_player_id[index]) {
                document.getElementsByClassName('text_price')[parseInt(this.houses_player_num[index]) - 1 + 6].style.color = "black";
                document.getElementsByClassName('text_round')[parseInt(this.houses_player_num[index]) - 1 ].style.color = "black";

                document.getElementsByClassName('text_price')[parseInt(this.houses_player_num[index]) - 1  + 6].style.opacity = 1;
                document.getElementsByClassName('text_round')[parseInt(this.houses_player_num[index]) - 1 ].style.opacity = 1;

                document.getElementsByClassName('image_house')[parseInt(this.houses_player_num[index]) - 1 ].style.opacity = 1;

            }else if (this.round_player_id == this.houses_player_id[index]) {
                document.getElementsByClassName('text_price')[parseInt(this.houses_player_num[index]) - 1  + 6].style.color = "black";
                document.getElementsByClassName('text_round')[parseInt(this.houses_player_num[index]) - 1 ].style.color = "black";

                document.getElementsByClassName('text_price')[parseInt(this.houses_player_num[index]) - 1  + 6].style.opacity = 1;
                document.getElementsByClassName('text_round')[parseInt(this.houses_player_num[index]) - 1 ].style.opacity = 1;

                document.getElementsByClassName('image_house')[parseInt(this.houses_player_num[index]) - 1 ].style.opacity = 1;

            }else{
                document.getElementsByClassName('text_price')[parseInt(this.houses_player_num[index]) - 1  + 6].style.color = "black";
                document.getElementsByClassName('text_round')[parseInt(this.houses_player_num[index]) - 1 ].style.color = "black";

                document.getElementsByClassName('text_price')[parseInt(this.houses_player_num[index]) - 1  + 6].style.opacity = 0.5;
                document.getElementsByClassName('text_round')[parseInt(this.houses_player_num[index]) - 1 ].style.opacity = 0.5;

                document.getElementsByClassName('image_house')[parseInt(this.houses_player_num[index]) - 1 ].style.opacity = 0.5;

            }
        }

        if (this.round_rented == 1){

            if (this.round_player_id == this.current_player_id){
                if (this.round_price_accepted == 1){
                    new_message_rent_single_personal = message_rent_single_personal.replace("{price}",this.round_price_rented);
                    $('#message_rent').html(new_message_rent_single_personal);
                }

                if (this.round_price_accepted > 1) {
                    new_message_rent_multiple_personal = message_rent_multiple_personal.replace("{price}", this.round_price_rented);
                    new_message_rent_multiple_personal = new_message_rent_multiple_personal.replace("{players}", this.round_price_accepted);
                    new_message_rent_multiple_personal = new_message_rent_multiple_personal.replace("{player}", this.round_player_num);
                    $('#message_rent').html(new_message_rent_multiple_personal);
                }
            }else{
                if (this.round_price_accepted == 1) {
                    new_message_rent_single = message_rent_single.replace("{player}", this.round_player_num);
                    new_message_rent_single = new_message_rent_single.replace("{price}", this.round_price_rented);
                    $('#message_rent').html(new_message_rent_single);
                }

                if (this.round_price_accepted > 1) {
                    new_message_rent_multiple = message_rent_multiple.replace("{players}", this.round_price_accepted);
                    new_message_rent_multiple = new_message_rent_multiple.replace("{player}", this.round_player_num);
                    new_message_rent_multiple = new_message_rent_multiple.replace("{price}", this.round_price_rented);
                    $('#message_rent').html(new_message_rent_multiple);
                }
            }

            // Icon up or equal (treatment with limit)
            console.log('Round rented and Increment: ' + this.round_increment)
            if (this.round_increment == 1){

                new_message_market_increment = message_market_increment.replace("{increment}",  this.increment);
                new_message_market_increment = new_message_market_increment.replace("{price_rented}", this.round_price_rented);
                new_message_market_increment = new_message_market_increment.replace("{price_market}", this.round_price_market);
                $('#message_market').html(new_message_market_increment);

                document.getElementsByClassName('image_up')[0].style.visibility = 'visible';
                document.getElementsByClassName('image_down')[0].style.visibility = 'hidden';
                document.getElementsByClassName('image_equal')[0].style.visibility = 'hidden';
            }
            else if (this.round_increment == 0){

                new_message_market_high_limit = message_market_high_limit.replace("{high_limit}", this.limit_high);
                $('#message_market').html(new_message_market_high_limit);

                document.getElementsByClassName('image_up')[0].style.visibility = 'hidden';
                document.getElementsByClassName('image_down')[0].style.visibility = 'hidden';
                document.getElementsByClassName('image_equal')[0].style.visibility = 'visible';
            }
            else if (this.round_increment == -1){

                document.getElementsByClassName('image_up')[0].style.visibility = 'hidden';
                document.getElementsByClassName('image_down')[0].style.visibility = 'visible';
                document.getElementsByClassName('image_equal')[0].style.visibility = 'hidden';
            }


        }else{

            $('#message_rent').html(message_no_rent);
            console.log('Round not rented and Increment: ' + this.round_increment)
            // Icon up or equal (treatment with limit)
            if (this.round_increment == -1){
                new_message_market_decrement = message_market_decrement.replace("{increment}", this.increment);
                new_message_market_decrement = new_message_market_decrement.replace("{price_final}", this.round_price_final);
                new_message_market_decrement = new_message_market_decrement.replace("{price_initial}", this.round_price_initial);
                $('#message_market').html(new_message_market_decrement);

                document.getElementsByClassName('image_up')[0].style.visibility = 'hidden';
                document.getElementsByClassName('image_down')[0].style.visibility = 'visible';
                document.getElementsByClassName('image_equal')[0].style.visibility = 'hidden';
            }
            else if (this.round_increment == 0){

                new_message_market_low_limit = message_market_low_limit.replace("{subsidy}", this.subsidy);
                new_message_market_low_limit = new_message_market_low_limit.replace("{tax}", this.tax);
                $('#message_market').html(new_message_market_low_limit);


                document.getElementsByClassName('image_up')[0].style.visibility = 'hidden';
                document.getElementsByClassName('image_down')[0].style.visibility = 'hidden';
                document.getElementsByClassName('image_equal')[0].style.visibility = 'visible';
            }
            else if (this.round_increment == 1){

                document.getElementsByClassName('image_up')[0].style.visibility = 'visible';
                document.getElementsByClassName('image_down')[0].style.visibility = 'hidden';
                document.getElementsByClassName('image_equal')[0].style.visibility = 'hidden';
            }
        }

        $('#text-house-revalue').html(this.round_price_final + "€");

        if (this.current_player_house == false){
            new_message_no_rent_status = message_no_rent_status.replace("{players}", (6 - this.houses_player_num.length).toString());
            new_message_no_rent_status = new_message_no_rent_status.replace("{houses}", (6 - this.houses_player_num.length).toString());
            new_message_no_rent_status = new_message_no_rent_status.replace("{rounds}", (12 - parseInt(this.round_round_num)).toString());
            $('#message_no_rent_status').html(new_message_no_rent_status);
            $('#message_no_rent_status').show();
        }else{
            $('#message_no_rent_status').hide();
        }
    },

    countdown_next_round: function() {
        if (this.next_round_time>0) {
            $('#nextround_time').html(Math.ceil(this.next_round_time/1000));
            this.next_round_time = this.next_round_time - 1000;
            setTimeout(function(){ game.countdown_next_round() }, 1000);
        } else {
            $("#ronda-modal").modal('hide');
            game.start_next_round();
        }
    },


    //////////////////////////////////////////////////////////////////////////////////////////
    /////////////////////////  FUNCIONS AJAX SERVER   ////////////////////////////////////////
    //////////////////////////////////////////////////////////////////////////////////////////

    // FUNCIO PER A RECOLLIR LES DADES DEL SERVER
    demanar_dades: function() {
        //console.log(this.user_id);
        $.ajax({
            url: '/es/ws/demanar_dades/'+this.user_id+'/',
            success: function(data) {
                if (data.playing=="false") {
                    setTimeout(function(){game.demanar_dades();}, 1000);
                } else {
                    $("#welcome-modal").modal('hide');
                    game.start_game(data);
                }
            },
            error: function(data) {
                setTimeout(function(){game.demanar_dades();}, 1000);
            }
        });
    },

    //Funcio per a enviar el resultat de la ronda
    enviar_accio: function(user, ronda, accio) {
        $.ajax({
            url: '/es/ws/enviar_accio/'+user+'/'+ronda+'/'+accio+'/',
            success: function(data) {
                if (data.saved == "ok") {
                } else {
                    game.enviar_accio(user, ronda, accio);
                }
            },
            error: function(){
                game.enviar_accio(user, ronda, accio);
            }
        });
    },

    //Funcio per a obtenir el resultat del torn
    demanar_resultat: function() {
        console.log('ID: ' + this.user_id),
        console.log('Round: ' + game.current_round),
        $.ajax({
            url: '/es/ws/demanar_resultat/'+this.user_id+'/'+game.current_round+'/',
            success: function(data) {
                if (data.correcte && !data.playing) {
                    $('#final-modal').modal({ backdrop: 'static', keyboard: true }).modal('show');
                } else if (data.correcte && data.ronda_acabada) {
                    game.end_round(data);
                } else {
                    setTimeout(function(){ game.demanar_resultat() }, 500);
                }
            },
            error: function(data) {
                console.log('Error game.demanar_resultats')
                setTimeout(function(){ game.demanar_resultat() }, 500);
            }
        });
    },

    //Demanar resultats de final de ronda
    demanar_final_ronda: function() {
        console.log('Final Round')
        $.ajax({
            url: '/es/ws/demanar_resultat/'+this.user_id+'/'+game.current_round+'/',
            success: function(data) {
                if (data.correcte && data.ronda_acabada) {
                    game.end_round(data);
                } else {
                    setTimeout(function(){ game.demanar_final_ronda() }, 2000);
                }
            },
            error: function(data) {
                console.log('Error game.demanar_resultats')
                setTimeout(function(){ game.demanar_final_ronda() }, 2000);
            }
        });
    }

};

game = new Game();

$(document).ready(function() {

    $("#final-modal").on("shown.bs.modal", function() {    // wire up the OK button to dismiss the modal when shown
        $("#final-modal-fi").on("click", function(e) {
            $("#final-modal").modal('hide').on("hidden.bs.modal", function() {
                // ToDo: once the game finished go to survey or results
                //if (game.experiment == 'Aigua') {
                    window.location.href = '/' + game.lang + '/user/surveyfinal1';
                //}else{
                //    window.location.href = '/'+ game.lang + '/user/resultats_clima';
                //}
            });
        });
    });

    $("#button-0").on("pushed", function(e) {
        //enviar missatge al server que hem apretat C
        $('#esperar-modal').modal({ backdrop: 'static', keyboard: true }).modal('show');
        game.resposta = true;
        console.log(game.current_round)
        game.enviar_accio(game.user_id, game.current_round, 0);
        game.demanar_resultat();
    });

    $("#button-1").on("pushed", function(e) {
        //enviar missatge al server que hem apretat C
        $('#esperar-modal').modal({ backdrop: 'static', keyboard: true }).modal('show');
        game.resposta = true;
        console.log(game.current_round)
        game.enviar_accio(game.user_id, game.current_round, 1);
        game.demanar_resultat();
    });

    $('#welcome-modal').modal({ backdrop: 'static', keyboard: true }).modal('show');
    game.demanar_dades();
});


