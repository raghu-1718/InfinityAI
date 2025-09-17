import { createTheme } from '@mui/material/styles';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#4A90E2' },
    secondary: { main: '#FFD93D' },
    background: { default: '#131A26', paper: '#181F2D' },
    text: { primary: '#fff' }
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
    h5: { fontWeight: 700, letterSpacing: 1.2 }
  },
  shape: { borderRadius: 16 }
});

export default darkTheme;
