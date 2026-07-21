/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import {KsDashboardNinja} from "@ks_dashboard_ninja/js/ks_dashboard_ninja_new";
import { _t } from "@web/core/l10n/translation";
import { renderToElement,renderToString } from "@web/core/utils/render";
import { isBrowserChrome, isMobileOS } from "@web/core/browser/feature_detection";
import { Ksdashboardtile } from '@ks_dashboard_ninja/components/ks_dashboard_tile_view/ks_dashboard_tile';

patch(KsDashboardNinja.prototype,{
    setup(){
        super.setup()
    },

        ks_dash_print(id){
            var self = this;
            var ks_dashboard_name = self.ks_dashboard_data.name
            setTimeout(function () {
            window.scrollTo(0, 0);
            html2canvas(document.querySelector('.ks_dashboard_item_content'), {useCORS: true, allowTaint: false}).then(function(canvas){
            window.jsPDF = window.jspdf.jsPDF;
            var pdf = new jsPDF("p", "mm", "a4");
            var ks_img = canvas.toDataURL("image/jpeg", 0.90);
            var ks_props= pdf.getImageProperties(ks_img);
            var KspageHeight = 300;
            var KspageWidth = pdf.internal.pageSize.getWidth();
            var ksheight = (ks_props.height * KspageWidth) / ks_props.width;
            var ksheightLeft = ksheight;
            var position = 0;

            pdf.addImage(ks_img,'JPEG', 0, 0, KspageWidth, ksheight, 'FAST');
            ksheightLeft -= KspageHeight;
            while (ksheightLeft >= 0) {
                position = ksheightLeft - ksheight;
                pdf.addPage();
                pdf.addImage(ks_img, 'JPEG', 0, position,  KspageWidth, ksheight, 'FAST');
                ksheightLeft -= KspageHeight;
            };
            pdf.save(ks_dashboard_name + '.pdf');
        })
        },500);
        },

        ks_send_mail(ev) {
            var self = this;
            var ks_dashboard_name = self.ks_dashboard_data.name
            setTimeout(function () {
            $('.fa-envelope').addClass('d-none')
            $('.fa-spinner').removeClass('d-none');


            window.scrollTo(0, 0);
            html2canvas(document.querySelector('.ks_dashboard_item_content'), {useCORS: true, allowTaint: false}).then(function(canvas){
            window.jsPDF = window.jspdf.jsPDF;
            var pdf = new jsPDF("p", "mm", "a4");
            var ks_img = canvas.toDataURL("image/jpeg", 0.90);
            var ks_props= pdf.getImageProperties(ks_img);
            var KspageHeight = 300;
            var KspageWidth = pdf.internal.pageSize.getWidth();
            var ksheight = (ks_props.height * KspageWidth) / ks_props.width;
            var ksheightLeft = ksheight;
            var position = 0;

            pdf.addImage(ks_img,'JPEG', 0, 0, KspageWidth, ksheight, 'FAST');
            ksheightLeft -= KspageHeight;
            while (ksheightLeft >= 0) {
                position = ksheightLeft - ksheight;
                pdf.addPage();
                pdf.addImage(ks_img, 'JPEG', 0, position,  KspageWidth, ksheight, 'FAST');
                ksheightLeft -= KspageHeight;
            };
//            pdf.save(ks_dashboard_name + '.pdf');
            const file = pdf.output()
            const base64String = btoa(file)

//            localStorage.setItem(ks_dashboard_name + '.pdf',file);

            $.when(base64String).then(function(){
                self._rpc("/web/dataset/call_kw/ks_dashboard_ninja.board/ks_dashboard_send_mail",{
                    model: 'ks_dashboard_ninja.board',
                    method: 'ks_dashboard_send_mail',
                    args: [
                        [parseInt(self.ks_dashboard_id)],base64String

                    ],

                    kwargs:{}
                }).then(function(res){
                    $('.fa-envelope').removeClass('d-none')
                    $('.fa-spinner').addClass('d-none');
                    if (res['ks_is_send']){
                        var msg = res['ks_massage']
                            self.notification.add(_t(msg),{
                                title:_t("Success"),
                                type: 'info',
                            });

                    }else{
                        var msg = res['ks_massage']
                        self.notification.add(_t(msg),{
                                title:_t("Fail"),
                                type: 'warning',
                            });

                    }
                });
             })
        })
        },500);

        },

        ksStopTvDashboard(e){
            $('.owl-carousel').owlCarousel('destroy');
             $('.ks_float_tv').addClass('d-none');
             this.ksAllowItemClick = true;

        },

        startTvDashboard(e){
            var self = this;
            $('.owl-carousel').find(".grid-stack-item.ks_chart_container").each(function(index,item){
                $(item).removeClass("grid-stack-item")
                $(item).addClass("ks-tv-item")
                item.style.pointerEvents = 'none'
                $(item).find(".ks_dashboard_item_button_container").remove()
            })
            $('.owl-carousel').find(".ks_dashboard_item_button_container").each(function(index,item){
                $(item).remove()
            })
            $('.owl-carousel').find(".ks_list_view_container").each(function(index,item){
                $(item).parent().addClass("ks-tv-item")
            })


            var speed = self.ks_dashboard_data.ks_croessel_speed ? parseInt(self.ks_dashboard_data.ks_croessel_speed) : 5000
            $('.ks_float_tv').removeClass('d-none');

            $('.owl-carousel').owlCarousel({
                rtl: $('.o_rtl').length>0,
                loop:true,
                nav:true,
                dots:false,
                items : 1,
                margin:10,
                autoplay:true,
                autoplayTimeout:speed,
                responsiveClass: true,
                autoplayHoverPause: true,
                navText:['<i class="fa fa fa-angle-left"></i>','<i class="fa fa fa-angle-right"></i>'],
            });
            if (self.ks_dashboard_data.ks_dashboard_background_color != undefined){
                $('.owl-carousel').find('.ks_chart_container').each(function() {
                    var currentElement = $(this);
                    if (self.ks_dashboard_data.ks_dark_mode_enable == true){
                        currentElement.children().css({"backgroundColor": '#2a2a2a'});
                    }
                    else{
                        currentElement.children().css({"backgroundColor": self.ks_dashboard_data.ks_dashboard_background_color.split(',')[0]});
                    }
                });
            }
        },

         dashboard_mount(){
            var self = this;
            super.dashboard_mount()
            self.ksRenderTvDashboardItems(self.state.ks_dashboard_items );

        },

        ksRenderTvDashboardItems(items){
            var self = this;
            this.ks_dashboard_data = self.ks_dashboard_data
            this.tiles = [];
            this.kpi = [];
            this.graph = [];
            this.to_do = [];
            for (var i = 0; i < items.length; i++) {
                if (items[i].ks_dashboard_item_type === 'ks_tile') {
                    this.tiles.push(items[i]);
                } else if (items[i].ks_dashboard_item_type === 'ks_kpi') {
                    this.kpi.push(items[i]);
                } else if (items[i].ks_dashboard_item_type === 'ks_to_do') {
                    this.to_do.push(items[i])
               } else {
                    this.graph.push(items[i])
               }
            }
            self._renderTiles();
            self._renderKPi();

        },
        _renderTiles(){
            var self = this;
            this.tile_item = []
            if (isMobileOS()){
            var count  =  Math.round(this.tiles.length)
            var kscontainer =[]
            for(var i = 1; i<= count; i++){
                var ks_tiles = this.tiles.splice(0,1);
                var container = [];
                for (var j = 0; j<ks_tiles.length; j++){
                    var item_data = ks_tiles[j];
                        item_data.ks_tv_play = true
                        self.ksAllowItemClick = false

                        container.push(item_data);
                }
                kscontainer.push(container)
                this.tiles.push(kscontainer)
            }
            }else{
            var count  =  Math.round(this.tiles.length/2)
            var kscontainer =  []
            for(var i = 1; i<= count; i++){
                var ks_tiles = this.tiles.splice(0,2);
                var container = [];
                for (var j = 0; j<ks_tiles.length; j++){
                    var item_data = ks_tiles[j];
                        item_data.ks_tv_play = true
                        self.ksAllowItemClick = false

                    container.push(item_data);
                }
                kscontainer.push(container)
                if (i%2 === 0){
                    this.tile_item.push(kscontainer);
                    kscontainer = []
                }
            }
            if(kscontainer.length){
                this.tile_item.push(kscontainer);
            }
            }

        },
        _renderKPi(){
            var self = this;
            this.kpi_item = [];
            if (isMobileOS()){
            var count  =  Math.round(this.kpi.length);
            for(var i = 1; i<= count; i++){
                var kscontainer = []
                var ks_tiles = this.kpi.splice(0,1)
                 for (var j = 0; j<ks_tiles.length; j++){
                    var item_data = ks_tiles[j];
                    item_data.ks_tv_play = true
                    self.ksAllowItemClick = false
                    kscontainer.push(item_data);
                }
                this.kpi_item.push(kscontainer);
            }
            }else{
            var count  =  Math.round(this.kpi.length/2);
            for(var i = 1; i<= count; i++){
                var kscontainer = []
                var ks_tiles = this.kpi.splice(0,2)
                 for (var j = 0; j<ks_tiles.length; j++){
                    var item_data = ks_tiles[j];
                    item_data.ks_tv_play = true
                    self.ksAllowItemClick = false
                    kscontainer.push(item_data);
                }
                this.kpi_item.push(kscontainer);
            }
            }
        },


});

