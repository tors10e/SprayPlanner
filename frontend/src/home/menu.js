import React from 'react';
import { Container, Col, Row, Image } from 'react-bootstrap';
import { ClickableOverlayCard, OverlayCard } from '../components/card';

import GreenGrapes from "../images/green_grapes_800x540.jpg";
import SunsetRidge from "../images/sunset_ridge_800x541.jpg";
import MountainFog from "../images/foggy_mtns_800x537.jpg";
import PavilionGlow from "../images/pavilion_glow_800x540.jpg";
import DiningOut from "../images/dining_out_800x531.jpg";
import NightVines from "../images/night_vines_800.jpg";

export function Menu(props) {
    return (
    <div class="row">
        <div class="col-sm"><ClickableOverlayCard card_image={PavilionGlow} card_title="WEDDINGS" url="/weddings"/></div>
        <div class="col-sm"><ClickableOverlayCard card_image={NightVines} card_title="OVERNIGHTING" url="/overnighting"/> </div>
        <div class="col-sm"><ClickableOverlayCard card_image={DiningOut} card_title="EVENTS" url="/events"/></div>
        <div class="w-100"></div>
        <div class="col-sm"><ClickableOverlayCard card_image={GreenGrapes} card_title="WINERY" url="/winery"/></div>
        <div class="col-sm"><ClickableOverlayCard card_image={SunsetRidge} card_title="TRAILS" url="/trails"/></div>
        <div class="col-sm"><ClickableOverlayCard card_image={MountainFog} card_title="PHOTO GALLERY"url="/gallery"/></div>
    </div>
    );
}

export default Menu;