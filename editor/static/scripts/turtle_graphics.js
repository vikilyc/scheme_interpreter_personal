import {states} from "./state_handler";
import {make, request_update} from "./event_handler";
import {draw} from "./turtle_graphics_worker";

export { register };

function register(myLayout) {
    myLayout.registerComponent('turtle_graphics', function (container, componentState) {
        container.getElement().html(`
        <div class="content">
            <div class="output-warning">
                This session may be out of date! Hit "Run" to refresh contents.
            </div>
            </div>
            <div class="drawing">
                <svg></svg>
            </div>
        </div>
        `);

        make(container, "turtle_graphics", componentState.id);

        let rawSVG = container.getElement().find(".drawing > svg").get(0);
        // svgPanZoom(rawSVG, {fit: false, zoomEnabled: true, center: false, controlIconsEnabled: true});
        let svg = SVG.adopt(rawSVG).size(container.width, container.height);

        let ready = false;

        container.getElement().find(".drawing").on("update", function () {
            let zoom;
            let pan;

            if (ready) {
                zoom = svgPanZoom(rawSVG).getZoom();
                pan = svgPanZoom(rawSVG).getPan();
                svgPanZoom(rawSVG).destroy();
            }
            svg.clear();
            ready = true;
            draw(states[componentState.id].moves);
            svgPanZoom(rawSVG, {fit: false, zoomEnabled: true, center: false, controlIconsEnabled: true});
            if (isNaN(zoom)) {
                svgPanZoom(rawSVG).reset();
            } else {
                svgPanZoom(rawSVG).zoom(zoom);
                svgPanZoom(rawSVG).pan(pan);
            }
        });

        container.getElement().find(".drawing").on("reset", function () {
            svgPanZoom(rawSVG).reset();
        });

        container.on("resize", function () {
            let zoom;
            let pan;

            if (ready) {
                zoom = svgPanZoom(rawSVG).getZoom();
                pan = svgPanZoom(rawSVG).getPan();
                svgPanZoom(rawSVG).destroy();
            }
            svg.size(container.width, container.height);
            svgPanZoom(rawSVG, {fit: false, zoomEnabled: true, center: false, controlIconsEnabled: true});
            if (isNaN(zoom)) {
                svgPanZoom(rawSVG).reset();
            } else {
                svgPanZoom(rawSVG).zoom(zoom);
                svgPanZoom(rawSVG).pan(pan);
            }

            ready = true;
        });

        container.on("shown", function () {
            request_update();
        })
    });
}