import ReactPixel from 'react-facebook-pixel';

const advancedMatching = { em: 'info@terraincognitavineyard.com' }; // optional, more info: https://developers.facebook.com/docs/facebook-pixel/advanced/advanced-matching
const options = {
  autoConfig: true, // set pixel's autoConfig. More info: https://developers.facebook.com/docs/facebook-pixel/advanced/
  debug: false, // enable logs
};
ReactPixel.init('1864226264131259', advancedMatching, options);

ReactPixel.pageView(); // For tracking page view
ReactPixel.track(event, data); // For tracking default events. More info about standard events: https://developers.facebook.com/docs/facebook-pixel/implementation/conversion-tracking#standard-events
ReactPixel.trackSingle('PixelId', event, data); // For tracking default events.
ReactPixel.trackCustom(event, data); // For tracking custom events. More info about custom events: https://developers.facebook.com/docs/facebook-pixel/implementation/conversion-tracking#custom-events
ReactPixel.trackSingleCustom('PixelId', event, data); // For tracking custom events.