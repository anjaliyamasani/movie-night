import React, { useState } from 'react';

const RecsSearchBox = () => {

    // state to store the search query inputted by user
    const [query, setQuery] = useState('');
    const [recommendations, setRecommendations] = useState([]);
    const [suggestions, setSuggestions] = useState([]);

    const fetchSuggestions = (input) => {
        if (input.length > 1) {
            fetch(`http://127.0.0.1:5000/api/search-movies?query=${encodeURIComponent(input)}`)
                .then(response => response.json())
                .then(data => {
                    setSuggestions(data);
                })
                .catch(error => console.error('Error fetching movie suggestions:', error));
        } else {
            setSuggestions([]);
        }
    };

    // handle input change
    const handleInputChange = (event) => {
        const input = event.target.value;
        setQuery(input);
        fetchSuggestions(input);
    };

    const handleSelect = (movie) => {
        setQuery(movie);
        setSuggestions([]);
        fetchRecommendations(movie);
    }

    const MoviePoster = ({ title, posterUrl }) => {
        return (
            <div>
                <h3>{title}</h3>
                {posterUrl ? (
                    <img src={posterUrl} alt={`${title} poster`} style={{ width: '200px' }} />
                ) : (
                    <p>No poster available</p>
                )}
            </div>
        );
    };

    const fetchRecommendations = (movie) => {
        fetch(`http://127.0.0.1:5000/api/recommendations?title=${encodeURIComponent(movie)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Received recommendations:', data);
                setRecommendations(data);
            })
            .catch(error => {
                console.error('Error fetching recommendations:', error);
            });
    }

    const handleSubmit = (event) => {
        event.preventDefault();
        console.log('Search query:', query);
        fetchRecommendations(query);
        // add logic here to handle search (python code)
        // Make the API call to Flask to get recommendations
    };
    
    return (
        <div>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    placeholder="Show me movies like..."
                    value={query}
                    onChange={handleInputChange}
                    style={{
                        width: '100%',
                        maxWidth: '330px',
                        padding: '8px',
                        marginTop: '10px',
                        fontSize: '16px',
                        fontFamily: 'Poppins'
                    }}
                />
                {/* Display dropdown with suggestions */}
                {suggestions.length > 0 && (
                    <ul style={{ border: '1px solid #ccc', maxHeight: '150px', overflowY: 'auto', padding: '0', margin: '0' }}>
                        {suggestions.map((movie, index) => (
                            <li 
                                key={index} 
                                onClick={() => handleSelect(movie)} 
                                style={{ padding: '8px', cursor: 'pointer', background: '#fff', borderBottom: '1px solid #ddd' }}
                            >
                                {movie}
                            </li>
                        ))}
                    </ul>
                )}
            </form>
            {/* Display the recommendations */}
            <div>
                <h3 style={{ color: 'white' }}>
                    Recommended Movies:
                </h3>
                <ul>
                    {recommendations.length === 0 ? (
                        <li style={{ color: 'white' }}>No recommendations yet</li>
                    ) : (
                        recommendations.map((movie, index) => (
                            <li key={index} style={{ color: 'white' }}>
                                <MoviePoster title={movie.title} posterUrl={movie.poster_url}/>
                            </li>
                        ))
                    )}
                </ul>
            </div>
        </div>
    );
};

export default RecsSearchBox;