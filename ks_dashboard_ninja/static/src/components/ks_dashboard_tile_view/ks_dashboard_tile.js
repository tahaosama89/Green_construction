/** @odoo-module **/
import { Component, onWillStart, useState ,onMounted, useEffect, onWillRender,useRef,onWillPatch, onRendered } from "@odoo/owl";
import {globalfunction } from '@ks_dashboard_ninja/js/ks_global_functions';
import { loadBundle } from "@web/core/assets";
import { isMobileOS } from "@web/core/browser/feature_detection";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

export class Ksdashboardtile extends Component{
    setup(){
        var self = this;
        this._rpc = useService("rpc");
        this.actionService = useService("action");
        this.ks_container_class = 'grid-stack-item';
        this.ks_inner_container_class = 'grid-stack-item-content';
        super.setup();
        this.state = useState({data_count:""})
        this.item = this.props.item
        this.ks_dashboard_data = this.props.dashboard_data
        this.prepare_item();
        var update_interval = this.props.dashboard_data.ks_set_interval
        useEffect(()=>{
            if (this.props.ksdatefilter != 'none'){
                this.ksFetchUpdateItem(this.item.id)
                this.props.ksdatefilter = 'none'
            }
            if (Object.keys(this.props.pre_defined_filter).length){
                if (this.props.pre_defined_filter?.item_ids?.includes(this.item.id)){
                    this.ksFetchUpdateItem(this.item.id)
                }
                this.props.pre_defined_filter = {}
            }
            if (update_interval){
                const interval = setInterval(() => {
                    this.ksFetchUpdateItem(this.item.id);
                }, update_interval);
                return () => clearInterval(interval);
            }
        })
    }

     ksFetchUpdateItem(item_id) {
            var self = this;
            return self._rpc("/web/dataset/call_kw/ks_dashboard_ninja.board/ks_fetch_item",{
                model: 'ks_dashboard_ninja.board',
                method: 'ks_fetch_item',
                args: [
                    [parseInt(item_id)], self.ks_dashboard_data.ks_dashboard_id,self.__owl__.parent.component.ksGetParamsForItemFetch(self.item.id)
                ],
                kwargs:{context:this.props.dashboard_data.context},
            }).then(function(new_item_data) {
                this.ks_dashboard_data.ks_item_data[item_id] = new_item_data[item_id];
                this.item = this.ks_dashboard_data.ks_item_data[item_id] ;
                this.prepare_item()
            }.bind(this));
        }


    get ks_dashboard_item_layout(){
        if (['layout1', 'layout2', 'layout3', 'layout4', 'layout5', 'layout6'].includes(this.item.ks_layout)){
            return 'ks_dashboard_item_' + this.item.ks_layout
        }else{
            return 'ks_dashboard_item_layout_default'
        }
    }

     _onKsItemClick(e){
        var self = this;
        //  To Handle only allow item to open when not clicking on item
        if (self.ksAllowItemClick) {



            e.preventDefault();
            if (e.target.title != "Customize Item") {
                var item_id = parseInt(e.currentTarget.firstElementChild.id);
                var item_data = self.ks_dashboard_data.ks_item_data[item_id];
                if (item_data && item_data.ks_show_records) {

                    if (item_data.action) {
                        if (!item_data.ks_is_client_action){
                            var action = Object.assign({}, item_data.action);
                            if (action.view_mode.includes('tree')) action.view_mode = action.view_mode.replace('tree', 'list');
                            for (var i = 0; i < action.views.length; i++) action.views[i][1].includes('tree') ? action.views[i][1] = action.views[i][1].replace('tree', 'list') : action.views[i][1];
                            action['domain'] = item_data.ks_domain || [];
                            action['search_view_id'] = [action.search_view_id, 'search']
                        }else{
                            var action = Object.assign({}, item_data.action[0]);
                            if (action.params){
                                action.params.default_active_id || 'mailbox_inbox';
                                }else{
                                    action.params = {
                                    'default_active_id': 'mailbox_inbox'
                                    }
                                    action.context = {}
                                    action.context.params = {
                                    'active_model': false
                                    };
                                }
                        }

                    } else {
                        var action = {
                            name: _t(item_data.name),
                            type: 'ir.actions.act_window',
                            res_model: item_data.ks_model_name,
                            domain: item_data.ks_domain || "[]",
                            views: [
                                [false, 'list'],
                                [false, 'form']
                            ],
                            view_mode: 'list',
                            target: 'current',
                        }
                    }

                    if (item_data.ks_is_client_action){
                        self.actionService.doAction(action,{})
                    }else{
                        self.actionService.doAction(action, {
                            on_reverse_breadcrumb: self.on_reverse_breadcrumb,
                        });
                    }
                }
            }
        } else {
            self.ksAllowItemClick = true;
        }
    }

    prepare_item() {
        var self = this;
        var ks_icon_url, item_view;
        var ks_rgba_background_color, ks_rgba_font_color, ks_rgba_default_icon_color,ks_rgba_button_color;
        var style_main_body, style_image_body_l2, style_domain_count_body, style_button_customize_body, style_button_delete_body;
        if (this.item.ks_multiplier_active){
            var ks_record_count = this.item.ks_record_count * this.item.ks_multiplier
            if (this.item.ks_unit){
                var ks_selection = this.item.ks_unit_selection;
                if (ks_selection === 'monetary') {
                    var ks_currency_id = this.item.ks_currency_id;
                    var ks_data = globalfunction._onKsGlobalFormatter(ks_record_count, this.item.ks_data_formatting, this.item.ks_precision_digits);
                    ks_data = globalfunction.ks_monetary(ks_data, ks_currency_id);
                    var data_count = ks_data;
                } else{
                    var ks_field = this.item.ks_chart_unit;
                    var data_count= ks_field+" "+globalfunction._onKsGlobalFormatter(ks_record_count, this.item.ks_data_formatting, this.item.ks_precision_digits);
                }
            }else {
                var data_count= globalfunction._onKsGlobalFormatter(ks_record_count, this.item.ks_data_formatting, this.item.ks_precision_digits);
            }
            var count = ks_record_count;
        }else{
            var ks_record_count = this.item.ks_record_count
            if (this.item.ks_unit){
                var ks_selection = this.item.ks_unit_selection;
                if (ks_selection === 'monetary') {
                    var ks_currency_id = this.item.ks_currency_id;
                    var ks_data = globalfunction._onKsGlobalFormatter(ks_record_count, this.item.ks_data_formatting, this.item.ks_precision_digits);
                    ks_data = globalfunction.ks_monetary(ks_data, ks_currency_id);
                    var data_count = ks_data;
                } else{
                    var ks_field = this.item.ks_chart_unit;
                    var data_count= ks_field+" "+globalfunction._onKsGlobalFormatter(ks_record_count, this.item.ks_data_formatting, this.item.ks_precision_digits);
                }
            }else {
                var data_count= globalfunction._onKsGlobalFormatter(ks_record_count, this.item.ks_data_formatting, this.item.ks_precision_digits);
            }
            var count = ks_record_count;
        }
        if (this.item.ks_icon_select == "Custom") {
            if (this.item.ks_icon[0]) {
                ks_icon_url = 'data:image/' + (self.file_type_magic_word[this.item.ks_icon[0]] || 'png') + ';base64,' + this.item.ks_icon;
            } else {
                ks_icon_url = false;
            }
        }

        this.item.ksIsDashboardManager = self.ks_dashboard_data.ks_dashboard_manager;
        this.item.ksIsUser = true;
//        if (this.item.ks_tv_play){
//            this.item.ksIsUser = false;
//        }
        ks_rgba_background_color = self._ks_get_rgba_format(this.item.ks_background_color);
        ks_rgba_font_color = self._ks_get_rgba_format(this.item.ks_font_color);
        this.ks_rgba_default_icon_color = self._ks_get_rgba_format(this.item.ks_default_icon_color);
        this.ks_rgba_button_color = self._ks_get_rgba_format(this.item.ks_button_color);
        if (this.item.ks_info){
            var ks_description = this.item.ks_info.split('\n');
            var ks_description = ks_description.filter(element => element !== '')
        }else {
            var ks_description = false;
        }
        this.ks_icon_url = ks_icon_url
        this.state.data_count = data_count
        this.count = count
        this.ks_info = ks_description
        this.ks_dashboard_list= self.ks_dashboard_data.ks_dashboard_list
        this.style_main_body = this._ksMainBodyStyle(ks_rgba_background_color, ks_rgba_font_color, this.item).background_style;
    }

    get style_image_body_l2(){
        return this._ksMainBodyStyle(this.ks_rgba_background_color, this.ks_rgba_font_color, this.item).style_image_body_l2;
    }

    get style_main_body_l4(){
        return "color : " + this.ks_rgba_font_color + ";border : solid;border-width : 1px;";
    }

    get style_image_body_l4(){
        return this._ksMainBodyStyle(this.ks_rgba_background_color, this.ks_rgba_font_color, this.item).background_style;
    }

    _ks_get_rgba_format(val){
        var rgba = val.split(',')[0].match(/[A-Za-z0-9]{2}/g);
        rgba = rgba.map(function(v) {
            return parseInt(v, 16)
        }).join(",");
        return "rgba(" + rgba + "," + val.split(',')[1] + ")";
    }

    _ksMainBodyStyle(ks_rgba_background_color, ks_rgba_font_color, tile){
        var background_style = "background-color:" + ks_rgba_background_color + ";color : " + ks_rgba_font_color + ";";
        var ks_rgba_dark_background_color_l2 = this._ks_get_rgba_format(this.ks_get_dark_color(tile.ks_background_color.split(',')[0], tile.ks_background_color.split(',')[1], -10));
        var style_image_body_l2 = "background-color:" + ks_rgba_dark_background_color_l2 + ";";
        return {
            'background_style': background_style,
            'style_image_body_l2': style_image_body_l2
        };
    }

    ks_get_dark_color(color, opacity, percent) {
        var num = parseInt(color.slice(1), 16),
            amt = Math.round(2.55 * percent),
            R = (num >> 16) + amt,
            G = (num >> 8 & 0x00FF) + amt,
            B = (num & 0x0000FF) + amt;
        return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 + (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 + (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1) + "," + opacity;
    }


};

Ksdashboardtile.props = {
    item: { type: Object, Optional:true},
    dashboard_data: { type: Object, Optional:true},
    ksdatefilter : {type:String,Optional:true},
    pre_defined_filter :{type:Object, Optional:true}
};

Ksdashboardtile.template = "ksdashboardtile";
