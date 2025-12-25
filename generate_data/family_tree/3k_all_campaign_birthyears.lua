if cm.name == "ep_eight_princes" then
	return;
end;

general_birth = {}

output("3k_all_campaign_birthyears.lua: Loading");


local function new_game()

end

local function initialise()

	output("Initialising character born manager")
    general_birth:register_historical_born()
end

cm:add_first_tick_callback_new(new_game);
cm:add_first_tick_callback(initialise); --Self register function

function general_birth:register_historical_born()
    -- register historical born
    MTUBornService:initialise();

    MTUBornService:register_born("xin_xianying", "female", "3k_general_water",
                                 "3k_main_template_historical_xin_xianying_hero_water", "ironic_template_historical_xin_pi_hero_water", 191);



    MTUBornService:register_born("cao_zhi", "male", "3k_general_water",
                                 "3k_main_template_historical_cao_zhi_hero_water", "3k_main_template_historical_cao_cao_hero_earth", 192); --192

    MTUBornService:register_born("liu_feng", "male", "3k_general_fire",
                                 "3k_main_template_historical_liu_feng_hero_fire", "3k_main_template_historical_liu_bei_hero_earth", 192); --192


    MTUBornService:register_born("luo_tong", "male", "3k_general_fire",
                                 "3k_main_template_historical_luo_tong_hero_fire", "3k_dlc04_template_historical_luo_jun_xiaoyuan_wood", 193); --192


    MTUBornService:register_born("cao_biao", "male", "3k_general_earth",
                                 "3k_main_template_historical_cao_biao_hero_earth", "3k_main_template_historical_cao_cao_hero_earth", 195); --195

    MTUBornService:register_born("wang_su", "male", "3k_general_water",
                                 "3k_main_template_historical_wang_su_hero_water", "3k_main_template_historical_wang_lang_hero_earth", 195);


--     MTUBornService:register_born("sun_huan", "male", "3k_general_fire",
--                                  "3k_main_template_historical_sun_huan_hero_fire", "ironic_template_historical_sun_jing_hero_wood", 195); --195

    MTUBornService:register_born("cao_jie", "female", "3k_general_earth",
                                 "3k_main_template_historical_lady_cao_jie_hero_earth", "3k_main_template_historical_cao_cao_hero_earth", 197); --197


    MTUBornService:register_born("cao_shuang", "male", "3k_general_wood",
                                 "3k_main_template_historical_cao_shuang_hero_wood", "3k_main_template_historical_cao_zhen_hero_earth", 203); --193

    MTUBornService:register_born("zhuge_ke", "male", "3k_general_earth",
                                 "3k_main_template_historical_zhuge_ke_hero_earth", "3k_main_template_historical_zhuge_jin_hero_water", 203); --203

    MTUBornService:register_born("cao_rui", "male", "3k_general_earth",
                                 "3k_main_template_historical_cao_rui_hero_earth", "3k_main_template_historical_cao_pi_hero_earth", 205); --205



    MTUBornService:register_born("sima_shi", "male", "3k_general_earth",
                                 "3k_main_template_historical_sima_shi_hero_earth", "3k_main_template_historical_sima_yi_hero_water", 208); --208

    MTUBornService:register_born("gongsun_yuan", "male", "3k_general_fire",
                                 "3k_main_template_historical_gongsun_yuan_hero_fire", "3k_main_template_historical_gongsun_kang_hero_earth", 210); --208

    MTUBornService:register_born("sima_zhao", "male", "3k_general_earth",
                                 "3k_main_template_historical_sima_zhao_hero_earth", "3k_main_template_historical_sima_yi_hero_water", 211); --211

    MTUBornService:register_born("sun_deng", "male", "3k_general_earth",
                                 "3k_main_template_historical_sun_deng_hero_earth", "3k_main_template_historical_sun_quan_hero_earth", 209); --209

    MTUBornService:register_born("cao_xi", "male", "3k_general_wood",
                                 "3k_main_template_historical_cao_xi_hero_wood", "3k_main_template_historical_cao_zhen_hero_earth", 210); --210

    MTUBornService:register_born("wang_yuanji", "female", "3k_general_earth",
                                 "3k_main_template_historical_wang_yuanji_hero_earth", "3k_main_template_historical_wang_su_hero_water", 217); --217

    MTUBornService:register_born("jia_chong", "male", "3k_general_water",
                                 "3k_main_template_historical_jia_chong_hero_water", "3k_main_template_historical_jia_kui_hero_fire", 217); --217

    MTUBornService:register_born("zhong_hui", "male", "3k_general_earth",
                                 "ironic_template_historical_zhong_hui_hero_earth", "3k_main_template_historical_zhong_yao_hero_water", 225); --227

    if cm:query_model():campaign_game_mode() == "romance" then


    MTUBornService:register_born("guan_suo", "male", "3k_general_wood",
                                 "ironic_template_fictional_guan_suo_hero_wood", "3k_main_template_historical_guan_yu_hero_wood", 207); --207


    end

	MTUBornService:register_born("liu_shan", "male", "3k_general_earth",
                                 "3k_main_template_historical_liu_shan_hero_earth", "3k_main_template_historical_liu_bei_hero_earth", 200);

    MTUBornService:register_born("guan_yinping", "female", "3k_general_wood",
                                 "3k_mtu_template_historical_lady_guan_yinping_hero_wood", "3k_main_template_historical_guan_yu_hero_wood", 190);

    MTUBornService:register_born("guan_xing", "male", "3k_general_wood",
                                 "3k_main_template_historical_guan_xing_hero_wood", "3k_main_template_historical_guan_yu_hero_wood", 193);

    MTUBornService:register_born("zhang_xingcai", "female", "3k_general_fire",
                                 "3k_mtu_template_historical_lady_zhang_xingcai_hero_fire", "3k_main_template_historical_zhang_fei_hero_fire", 190);

    MTUBornService:register_born("zhang_bao", "male", "3k_general_fire",
                                 "3k_mtu_template_historical_zhang_bao_hero_fire", "3k_main_template_historical_zhang_fei_hero_fire", 192);

	MTUBornService:register_born("guan_ping", "male", "3k_general_fire",
                                 "3k_main_template_historical_guan_ping_hero_fire", "3k_main_template_historical_guan_yu_hero_wood", 192);




end
