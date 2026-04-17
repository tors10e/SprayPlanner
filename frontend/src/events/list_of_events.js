
import easter_hunt from '../images/event_posters/2025_EasterHunt.jpg';
import mothers_day from '../images/event_posters/Mothersday2025-poster-2.jpg';
import yoga from '../images/event_posters/yoga_poster.jpg';
import horton from '../images/event_posters/BrianHorton.jpg';
import forestry_flier from "../images/event_posters/forestry_presentation.jpg";
import solstice_party from '../images/event_posters/2025_solstice_party.png';
import { ListGroup } from 'react-bootstrap';

// Example of an event with photo  ["March 3, 2023", "First day of the season we are back to being open!", pavilion_photo]
// Example of an event without photo  ["March 3, 2023", "First day of the season we are back to being open!"]
// Example of href ["December 1, 2023", ["Description of event", <a href="./events/warren-miller">Click here!</a>], some_photo],

export const events = [
  ["April 19, 2025",
    ["Easter Egg Hunt - Kids hunt starts at 4 pm and adult hunt starts at 6 pm.",
      <a target="_blank" href='https://square.link/u/P2qRh79U'> Click Here for Tickets!</a>
    ],
    easter_hunt
  ],
  ["May 11, 2025",
    ["Mother's day brunch 1:00 PM - 4 PM with Chef Alex Stein.",
      <a target="_blank" href='https://square.link/u/MAu0iOmP'> Click here to buy tickets!</a>
    ],
    mothers_day
  ],
  ["May 24, 2025",
    ["Live music with George James from 3-7pm followed by a Herpatology Walk and Talk at 730"]
  ],
  ["May 31, 2025",
    ["Yoga with Spencer Turk at 11 AM",
      <a target="_blank" href='https://square.link/u/1AChAfQU'> Click here to buy tickets!</a>
    ],
    yoga
  ],
  ["June 7, 2025",
    ["Guided hike at 11 AM followed by live music with George James at 3pm."]
  ],
  ["June 14, 2025",
    ["Live music with Brian Horton starting at 3 pm"
    ],
    horton
  ],
  ["June 28, 2025",
    ["Yoga with Spencer Turk at 11 AM",
      <a target="_blank" href='https://square.link/u/VH2gLaj0'> Click here to buy tickets!</a>
    ],
    yoga
  ],
  ["July 5, 2025",
    ["Guided hike at 11 AM followed by live music with Jake Hicks at 3pm."]
  ],
  ["July 26, 2025",
    [<ListGroup>
      <ListGroup.Item>11 AM Yoga with Spencer Turk <a target="_blank" href='https://square.link/u/M7AayuQC'>Click here to buy tickets</a></ListGroup.Item>
      <ListGroup.Item>3-7 PM Live music with George James</ListGroup.Item>
      <ListGroup.Item>3-6 PM Vineyard and Brew Candle Making Workshop <a target="_blank" href='https://square.link/u/KxKrceJD'> Click here to buy tickets</a></ListGroup.Item>
    </ListGroup>], yoga
  ],
  ["August 16, 2025",
    [<ListGroup>
      <ListGroup.Item>10 AM Woods hike and forestry presentation with Mike Oliver</ListGroup.Item>
    </ListGroup>
    ],forestry_flier
  ],
  ["August 9, 2025",
    [<ListGroup>
      <ListGroup.Item>3-7 PM Live music with Brian Horton</ListGroup.Item>
    </ListGroup>
    ], horton
  ],
  ["August 30, 2025",
    [<ListGroup>
      <ListGroup.Item>11 AM - 1230 PM Yoga with Spencer Turk <a target="_blank" href='https://square.link/u/iizkOFtT'>Click here to buy tickets</a></ListGroup.Item>
    </ListGroup>
    ], yoga
  ],
  ["August 31, 2025",
    [<ListGroup>
      <ListGroup.Item>3-7 PM Live music with Brian Horton</ListGroup.Item>
    </ListGroup>
    ], horton
  ],
  ["September 6, 2025",
    [<ListGroup>
      <ListGroup.Item>11 AM Guided woods hike</ListGroup.Item>
    </ListGroup>
    ],
  ],
  ["September 27, 2025",
    [<ListGroup>
      <ListGroup.Item>11 AM Yoga with Spencer Turk <a target="_blank" href='https://square.link/u/vyt6UYJf'>Click here to buy tickets</a></ListGroup.Item>
      <ListGroup.Item>3-7 PM Live music with Brian Horton</ListGroup.Item>
    </ListGroup>], yoga
  ],
    ["November 1, 2025",
    [<ListGroup>
      <ListGroup.Item>11 AM Guided hike</ListGroup.Item>
      <ListGroup.Item>3 PM Candle making class at the Roundhouse Tasting Room</ListGroup.Item>
      <ListGroup.Item>3-7 PM Live music with George James</ListGroup.Item>
    </ListGroup>]
  ],
    ["November 7, 2025",
    [<ListGroup>
      <ListGroup.Item><a href="https://artstour.org">Northeast Georgia Arts Tour</a></ListGroup.Item>
    </ListGroup>]
  ],
      ["November 8, 2025",
    [<ListGroup>
      <ListGroup.Item><a href="https://artstour.org">Northeast Georgia Arts Tour</a></ListGroup.Item>
    </ListGroup>]
  ],
      ["November 9, 2025",
    [<ListGroup>
      <ListGroup.Item><a href="https://artstour.org">Northeast Georgia Arts Tour</a></ListGroup.Item>
    </ListGroup>]
  ],
        ["November 29, 2025",
    [<ListGroup>
    <ListGroup.Item>11 AM Yoga with Spencer Turk <a target="_blank" href='https://square.link/u/cIOgJ1v4'>Click here to buy tickets</a></ListGroup.Item>
    </ListGroup>]
  ],
  ["December 6, 2025",
    [<ListGroup>
      <ListGroup.Item>11 AM Guided hike</ListGroup.Item>
    </ListGroup>]
  ],
  ,
  ["December 20, 2025",
    [<ListGroup>
      <ListGroup.Item>Join us for our Annual Solstice Party. This is a chance to hang out by the fire and watch the Yule Log burn while drinking Gluhwein and having some
        light food and snacks. Children are welcome to join in the fun! 5-8PM
      </ListGroup.Item>
    </ListGroup>], solstice_party
  ],
];





