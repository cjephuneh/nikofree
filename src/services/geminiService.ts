/**
 * Gemini API Service
 * Handles AI content generation using Google Gemini API
 */

const GEMINI_API_KEY = 'AIzaSyCMg5HbFMj5Hivs2qtXQkWjoLsKvBbYkSk';
// Using v1beta with gemini-2.0-flash model
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent';

export interface GenerateEventDescriptionParams {
  eventName: string;
  categories?: string[];
  interests?: string[];
  locationType?: 'physical' | 'online' | 'hybrid';
  locationName?: string;
  startDate?: string;
  startTime?: string;
}

export interface GeneratePartnerDescriptionParams {
  businessName: string;
  category?: string;
  location?: string;
  interests?: string[];
}

/**
 * Generate event description using Gemini API
 */
export const generateEventDescription = async (
  params: GenerateEventDescriptionParams
): Promise<string> => {
  try {
    const prompt = `Generate an engaging and professional event description for an event called "${params.eventName}". 

${params.categories && params.categories.length > 0 ? `Categories: ${params.categories.join(', ')}` : ''}
${params.interests && params.interests.length > 0 ? `Interests: ${params.interests.join(', ')}` : ''}
${params.locationType ? `Location Type: ${params.locationType}` : ''}
${params.locationName ? `Location: ${params.locationName}` : ''}
${params.startDate ? `Date: ${params.startDate}` : ''}
${params.startTime ? `Time: ${params.startTime}` : ''}

Generate a compelling event description (150-300 words) that:
- Is engaging and professional
- Highlights the key features and benefits
- Encourages attendance
- Is suitable for an event listing platform
- Uses clear, concise language

Return only the description text without any additional formatting or explanations.`;

    // Use v1beta with gemini-2.0-flash model and API key in header
    const response = await fetch(
      GEMINI_API_URL,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-goog-api-key': GEMINI_API_KEY,
        },
        body: JSON.stringify({
          contents: [
            {
              parts: [
                {
                  text: prompt,
                },
              ],
            },
          ],
        }),
      }
    );

    if (!response.ok) {
      throw new Error(`Gemini API error: ${response.statusText}`);
    }

    const data = await response.json();
    
    if (data.candidates && data.candidates[0] && data.candidates[0].content) {
      const generatedText = data.candidates[0].content.parts[0].text;
      return generatedText.trim();
    }

    throw new Error('No content generated from Gemini API');
  } catch (error) {
    console.error('Error generating event description:', error);
    throw error;
  }
};

/**
 * Generate partner business description using Gemini API
 */
export const generatePartnerDescription = async (
  params: GeneratePartnerDescriptionParams
): Promise<string> => {
  try {
    const prompt = `Generate a professional business description for "${params.businessName}".

${params.category ? `Category: ${params.category}` : ''}
${params.location ? `Location: ${params.location}` : ''}
${params.interests && params.interests.length > 0 ? `Interests: ${params.interests.join(', ')}` : ''}

Generate a compelling business description (100-200 words) that:
- Describes what the business does
- Highlights unique selling points
- Is professional and engaging
- Suitable for a partner application
- Uses clear, concise language

Return only the description text without any additional formatting or explanations.`;

    // Use v1beta with gemini-2.0-flash model and API key in header
    const response = await fetch(
      GEMINI_API_URL,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-goog-api-key': GEMINI_API_KEY,
        },
        body: JSON.stringify({
          contents: [
            {
              parts: [
                {
                  text: prompt,
                },
              ],
            },
          ],
        }),
      }
    );

    if (!response.ok) {
      throw new Error(`Gemini API error: ${response.statusText}`);
    }

    const data = await response.json();
    
    if (data.candidates && data.candidates[0] && data.candidates[0].content) {
      const generatedText = data.candidates[0].content.parts[0].text;
      return generatedText.trim();
    }

    throw new Error('No content generated from Gemini API');
  } catch (error) {
    console.error('Error generating partner description:', error);
    throw error;
  }
};

