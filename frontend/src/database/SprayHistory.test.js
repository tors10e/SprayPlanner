import React from 'react';
import { render, screen, act } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import SprayHistory from './SprayHistory';

// Mock global fetch
beforeEach(() => {
  global.fetch = jest.fn();
});

test('renders SprayHistory with Spray #7 successfully', async () => {
  const mockHistory = [
    {
      "id": 33,
      "Spray #": 7,
      "Block ": "cs",
      "Date": "07/08/26",
      "End Time": "1200",
      "Pesticide": "Vivando",
      "Group": "U8",
      "Dose/acre": 12.0,
      "Rate Units": "fl oz",
      "Liters/Acre": 200.0,
      "Notes": "Test notes"
    }
  ];

  global.fetch.mockImplementation((url) => {
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve(mockHistory),
      text: () => Promise.resolve(JSON.stringify(mockHistory))
    });
  });

  await act(async () => {
    render(
      <BrowserRouter>
        <SprayHistory />
      </BrowserRouter>
    );
  });

  // Verify that "Spray #7" is rendered on the screen
  const headerElement = screen.getByText(/Spray #7/i);
  expect(headerElement).toBeInTheDocument();
  
  // Verify that "Block: cs" is rendered
  const blockElement = screen.getByText(/Block: cs/i);
  expect(blockElement).toBeInTheDocument();

  // Verify that "Vivando" is rendered
  const pesticideElement = screen.getByText(/Vivando/i);
  expect(pesticideElement).toBeInTheDocument();
  
  console.log("Rendered HTML output:\n" + document.body.innerHTML);
});
