import React, { useState, useRef, useEffect } from 'react';
import { Box, Paper, TextField, IconButton, Typography, AppBar, Toolbar, Avatar, Container } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { marked } from 'marked';

interface Message {
  sender: 'user' | 'bot';
  text: string;
}

const BOT_AVATAR = <Avatar sx={{ bgcolor: '#1976d2' }}>B</Avatar>;
const USER_AVATAR = <Avatar sx={{ bgcolor: '#43a047' }}>U</Avatar>;

function renderMarkdown(md: string) {
  return { __html: marked(md, { breaks: true }) };
}

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    { sender: 'bot', text: 'Hi! I am your Disaster & Weather Assistant. How can I help you today?' }
  ]);
  const [input, setInput] = useState('');
  const [pending, setPending] = useState<any>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    setMessages(msgs => [...msgs, { sender: 'user', text: input }]);
    const userInput = input;
    setInput('');
    try {
      const res = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userInput, pending })
      });
      const data = await res.json();
      setMessages(msgs => [...msgs, { sender: 'bot', text: data.response }]);
      if (typeof data.response === 'string' && data.response.includes('Please specify a location')) {
        setPending((prev: any) => prev || pending || { query: userInput });
      } else {
        setPending(null);
      }
    } catch (e) {
      setMessages(msgs => [...msgs, { sender: 'bot', text: 'Sorry, there was an error connecting to the server.' }]);
      setPending(null);
    }
  };

  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement | HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <Box sx={{ bgcolor: '#f5f7fa', minHeight: '100vh' }}>
      <AppBar position="static" color="primary">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Disaster & Weather Chatbot
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="sm" sx={{ py: 4 }}>
        <Paper elevation={3} sx={{ p: 2, minHeight: 500, display: 'flex', flexDirection: 'column', bgcolor: '#fff' }}>
          <Box sx={{ flex: 1, overflowY: 'auto', mb: 2 }}>
            {messages.map((msg, idx) => (
              <Box key={idx} sx={{ display: 'flex', mb: 2, flexDirection: msg.sender === 'user' ? 'row-reverse' : 'row', alignItems: 'flex-end' }}>
                {msg.sender === 'user' ? USER_AVATAR : BOT_AVATAR}
                <Box sx={{ mx: 1, maxWidth: '75%' }}>
                  <Paper sx={{ p: 1.5, bgcolor: msg.sender === 'user' ? '#e8f5e9' : '#e3f2fd', borderRadius: 2 }}>
                    {msg.sender === 'bot' ? (
                      <Typography
                        variant="body1"
                        component="span"
                        sx={{ wordBreak: 'break-word' }}
                        dangerouslySetInnerHTML={renderMarkdown(msg.text)}
                      />
                    ) : (
                      <Typography variant="body1">{msg.text}</Typography>
                    )}
                  </Paper>
                </Box>
              </Box>
            ))}
            <div ref={chatEndRef} />
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TextField
              fullWidth
              multiline
              minRows={1}
              maxRows={4}
              placeholder="Type your message..."
              value={input}
              onChange={e => setInput(e.target.value)}
              inputProps={{
                onKeyDown: handleInputKeyDown
              }}
            />
            <IconButton color="primary" onClick={sendMessage} disabled={!input.trim()}>
              <SendIcon />
            </IconButton>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};

export default App;
