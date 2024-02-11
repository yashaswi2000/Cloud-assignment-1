export const handler = async (event) => {
    // TODO implement
    const response = {
      statusCode: 200,
      messages: [
          {
            type: "unstructured",
            unstructured: {
             id: "temp",
             text: "I’m still under development. Please come back later.",
             timestamp: "12/03/2024"
            }
          }
        ],
    };
    return response;
  };
  