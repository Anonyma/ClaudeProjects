import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Play, Pause, Square, Clock, Target, BarChart3, Lightbulb, Settings, ChevronLeft, ChevronRight, FileText, Calendar, TrendingUp, Timer, Check, X, Edit3, Save, Trash2, Plus } from 'lucide-react';

// Storage utilities
const storage = {
  get: (key, defaultValue) => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch {
      return defaultValue;
    }
  },
  set: (key, value) => {
    localStorage.setItem(key, JSON.stringify(value));
  }
};

// Common words list for separate counting
const COMMON_WORDS = new Set([
  'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
  'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has', 'had',
  'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
  'shall', 'can', 'it', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she',
  'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our',
  'their', 'what', 'which', 'who', 'whom', 'when', 'where', 'why', 'how', 'if', 'then',
  'so', 'than', 'too', 'very', 'just', 'only', 'also', 'not', 'no', 'yes'
]);

// Clock progress visualization component
const ClockProgress = ({ progress, size = 120 }) => {
  const radius = (size - 12) / 2;
  const center = size / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference * (1 - Math.min(progress, 1));
  
  // Calculate hand positions
  const minuteAngle = (progress * 360) - 90;
  const minuteHandLength = radius * 0.7;
  const minuteX = center + minuteHandLength * Math.cos(minuteAngle * Math.PI / 180);
  const minuteY = center + minuteHandLength * Math.sin(minuteAngle * Math.PI / 180);
  
  return (
    <svg width={size} height={size} className="transform -rotate-90">
      {/* Background circle */}
      <circle
        cx={center}
        cy={center}
        r={radius}
        fill="none"
        stroke="#e5e7eb"
        strokeWidth="8"
      />
      {/* Progress arc */}
      <circle
        cx={center}
        cy={center}
        r={radius}
        fill="none"
        stroke={progress >= 1 ? "#22c55e" : "#3b82f6"}
        strokeWidth="8"
        strokeLinecap="round"
        strokeDasharray={circumference}
        strokeDashoffset={strokeDashoffset}
        style={{ transition: 'stroke-dashoffset 0.3s ease' }}
      />
      {/* Center dot */}
      <circle
        cx={center}
        cy={center}
        r="4"
        fill="#374151"
        className="transform rotate-90 origin-center"
      />
      {/* Progress hand */}
      <line
        x1={center}
        y1={center}
        x2={minuteX}
        y2={minuteY}
        stroke="#374151"
        strokeWidth="3"
        strokeLinecap="round"
        className="transform rotate-90 origin-center"
      />
    </svg>
  );
};

// Format time display
const formatTime = (seconds) => {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  if (hrs > 0) {
    return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

// Format date for display
const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric'
  });
};

// Main App Component
export default function WritingChallengeApp() {
  const [currentView, setCurrentView] = useState('write');
  const [settings, setSettings] = useState(() => storage.get('writingSettings', {
    goalType: 'words', // 'words', 'characters', 'time'
    wordGoal: 500,
    characterGoal: 2500,
    timeGoal: 20, // minutes
    countSpaces: true,
    countPunctuation: true,
    separateCommonWords: false,
    defaultPomodoro: 25, // minutes
  }));
  
  const [sessions, setSessions] = useState(() => storage.get('writingSessions', []));
  const [ideas, setIdeas] = useState(() => storage.get('writingIdeas', []));
  const [texts, setTexts] = useState(() => storage.get('writingTexts', []));
  
  // Current session state
  const [isWriting, setIsWriting] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [currentText, setCurrentText] = useState('');
  const [sessionStartTime, setSessionStartTime] = useState(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [timerTarget, setTimerTarget] = useState(null); // null = count up, number = countdown target
  const [showTitleModal, setShowTitleModal] = useState(false);
  const [pendingTitle, setPendingTitle] = useState('');
  
  const timerRef = useRef(null);
  const textareaRef = useRef(null);
  
  // Save settings to storage
  useEffect(() => {
    storage.set('writingSettings', settings);
  }, [settings]);
  
  // Save sessions to storage
  useEffect(() => {
    storage.set('writingSessions', sessions);
  }, [sessions]);
  
  // Save ideas to storage
  useEffect(() => {
    storage.set('writingIdeas', ideas);
  }, [ideas]);
  
  // Save texts to storage
  useEffect(() => {
    storage.set('writingTexts', texts);
  }, [texts]);
  
  // Timer effect
  useEffect(() => {
    if (isWriting && !isPaused) {
      timerRef.current = setInterval(() => {
        setElapsedSeconds(prev => prev + 1);
      }, 1000);
    } else {
      clearInterval(timerRef.current);
    }
    return () => clearInterval(timerRef.current);
  }, [isWriting, isPaused]);
  
  // Calculate text stats
  const getTextStats = useCallback((text) => {
    const words = text.trim().split(/\s+/).filter(w => w.length > 0);
    const wordCount = words.length;
    
    let commonWordCount = 0;
    let contentWordCount = 0;
    words.forEach(word => {
      if (COMMON_WORDS.has(word.toLowerCase().replace(/[^\w]/g, ''))) {
        commonWordCount++;
      } else {
        contentWordCount++;
      }
    });
    
    let charCount = text.length;
    if (!settings.countSpaces) {
      charCount = text.replace(/\s/g, '').length;
    }
    if (!settings.countPunctuation) {
      charCount = text.replace(/[^\w\s]/g, '').length;
      if (!settings.countSpaces) {
        charCount = text.replace(/[^\w]/g, '').length;
      }
    }
    
    return {
      words: wordCount,
      characters: charCount,
      commonWords: commonWordCount,
      contentWords: contentWordCount
    };
  }, [settings]);
  
  const stats = getTextStats(currentText);
  
  // Calculate progress
  const getProgress = useCallback(() => {
    if (settings.goalType === 'words') {
      return stats.words / settings.wordGoal;
    } else if (settings.goalType === 'characters') {
      return stats.characters / settings.characterGoal;
    } else {
      return elapsedSeconds / (settings.timeGoal * 60);
    }
  }, [settings, stats, elapsedSeconds]);
  
  const progress = getProgress();
  const goalMet = progress >= 1;
  
  // Timer progress (for pomodoro)
  const timerProgress = timerTarget ? elapsedSeconds / (timerTarget * 60) : 0;
  const pomodoroComplete = timerTarget && elapsedSeconds >= timerTarget * 60;
  
  // Start writing session
  const startSession = () => {
    setIsWriting(true);
    setIsPaused(false);
    setSessionStartTime(new Date().toISOString());
    setElapsedSeconds(0);
    setCurrentText('');
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };
  
  // Pause/Resume
  const togglePause = () => {
    setIsPaused(!isPaused);
  };
  
  // End session
  const endSession = () => {
    if (currentText.trim().length > 0) {
      setShowTitleModal(true);
      setPendingTitle('');
    } else {
      finalizeSession('');
    }
  };
  
  // Finalize and save session
  const finalizeSession = (title) => {
    const endTime = new Date().toISOString();
    const finalStats = getTextStats(currentText);
    
    const session = {
      id: Date.now(),
      startTime: sessionStartTime,
      endTime,
      duration: elapsedSeconds,
      words: finalStats.words,
      characters: finalStats.characters,
      contentWords: finalStats.contentWords,
      commonWords: finalStats.commonWords,
      goalType: settings.goalType,
      goalMet,
      goalValue: settings.goalType === 'words' ? settings.wordGoal : 
                 settings.goalType === 'characters' ? settings.characterGoal : 
                 settings.timeGoal
    };
    
    setSessions(prev => [...prev, session]);
    
    if (currentText.trim().length > 0) {
      const text = {
        id: Date.now(),
        title: title || `Untitled - ${formatDate(sessionStartTime)}`,
        content: currentText,
        createdAt: sessionStartTime,
        wordCount: finalStats.words,
        characterCount: finalStats.characters
      };
      setTexts(prev => [...prev, text]);
    }
    
    setIsWriting(false);
    setIsPaused(false);
    setCurrentText('');
    setElapsedSeconds(0);
    setSessionStartTime(null);
    setTimerTarget(null);
    setShowTitleModal(false);
  };
  
  // Set pomodoro timer
  const setPomodoro = (minutes) => {
    setTimerTarget(minutes);
    setElapsedSeconds(0);
  };
  
  // Navigation
  const NavButton = ({ view, icon: Icon, label }) => (
    <button
      onClick={() => setCurrentView(view)}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
        currentView === view 
          ? 'bg-blue-500 text-white' 
          : 'text-gray-600 hover:bg-gray-100'
      }`}
    >
      <Icon size={20} />
      <span className="hidden sm:inline">{label}</span>
    </button>
  );
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-800 flex items-center gap-2">
            <Edit3 className="text-blue-500" />
            <span className="hidden sm:inline">Writing Challenge</span>
          </h1>
          <div className="flex gap-2">
            <NavButton view="write" icon={FileText} label="Write" />
            <NavButton view="stats" icon={BarChart3} label="Stats" />
            <NavButton view="texts" icon={Calendar} label="Texts" />
            <NavButton view="ideas" icon={Lightbulb} label="Ideas" />
            <NavButton view="settings" icon={Settings} label="Settings" />
          </div>
        </div>
      </nav>
      
      <main className="max-w-6xl mx-auto p-4">
        {currentView === 'write' && (
          <WritingView
            isWriting={isWriting}
            isPaused={isPaused}
            currentText={currentText}
            setCurrentText={setCurrentText}
            stats={stats}
            progress={progress}
            goalMet={goalMet}
            elapsedSeconds={elapsedSeconds}
            timerTarget={timerTarget}
            timerProgress={timerProgress}
            pomodoroComplete={pomodoroComplete}
            settings={settings}
            startSession={startSession}
            togglePause={togglePause}
            endSession={endSession}
            setPomodoro={setPomodoro}
            textareaRef={textareaRef}
          />
        )}
        
        {currentView === 'stats' && (
          <StatsView sessions={sessions} settings={settings} />
        )}
        
        {currentView === 'texts' && (
          <TextsView texts={texts} setTexts={setTexts} />
        )}
        
        {currentView === 'ideas' && (
          <IdeasView ideas={ideas} setIdeas={setIdeas} />
        )}
        
        {currentView === 'settings' && (
          <SettingsView settings={settings} setSettings={setSettings} />
        )}
      </main>
      
      {/* Title Modal */}
      {showTitleModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">Save Your Writing</h3>
            <p className="text-gray-600 mb-4">
              Great work! You wrote {stats.words} words in {formatTime(elapsedSeconds)}.
              {goalMet && " 🎉 You met your goal!"}
            </p>
            <input
              type="text"
              placeholder="Give your text a title (optional)"
              value={pendingTitle}
              onChange={(e) => setPendingTitle(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === 'Enter') finalizeSession(pendingTitle);
              }}
            />
            <div className="flex gap-2">
              <button
                onClick={() => finalizeSession(pendingTitle)}
                className="flex-1 bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition-colors"
              >
                Save
              </button>
              <button
                onClick={() => {
                  setShowTitleModal(false);
                  setIsWriting(true);
                }}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Keep Writing
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Writing View Component
function WritingView({
  isWriting, isPaused, currentText, setCurrentText, stats, progress, goalMet,
  elapsedSeconds, timerTarget, timerProgress, pomodoroComplete, settings,
  startSession, togglePause, endSession, setPomodoro, textareaRef
}) {
  const [showTimerOptions, setShowTimerOptions] = useState(false);
  
  if (!isWriting) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[70vh]">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-2">Ready to Write?</h2>
          <p className="text-gray-600">
            Today's goal: {settings.goalType === 'words' && `${settings.wordGoal} words`}
            {settings.goalType === 'characters' && `${settings.characterGoal} characters`}
            {settings.goalType === 'time' && `${settings.timeGoal} minutes`}
          </p>
        </div>
        
        <button
          onClick={startSession}
          className="bg-blue-500 hover:bg-blue-600 text-white text-xl px-8 py-4 rounded-xl shadow-lg transition-all transform hover:scale-105 flex items-center gap-3"
        >
          <Play size={24} />
          Start Writing Session
        </button>
        
        <div className="mt-8 text-sm text-gray-500">
          Press to begin your focused writing time
        </div>
      </div>
    );
  }
  
  const goalLabel = settings.goalType === 'words' ? 'words' :
                    settings.goalType === 'characters' ? 'chars' : 'min';
  const goalTarget = settings.goalType === 'words' ? settings.wordGoal :
                     settings.goalType === 'characters' ? settings.characterGoal :
                     settings.timeGoal;
  const currentValue = settings.goalType === 'words' ? stats.words :
                       settings.goalType === 'characters' ? stats.characters :
                       Math.floor(elapsedSeconds / 60);
  
  return (
    <div className="flex flex-col h-[calc(100vh-120px)]">
      {/* Stats Bar */}
      <div className="bg-white rounded-xl shadow-sm p-4 mb-4">
        <div className="flex items-center justify-between flex-wrap gap-4">
          {/* Progress Clock */}
          <div className="flex items-center gap-4">
            <ClockProgress progress={progress} size={80} />
            <div>
              <div className={`text-2xl font-bold ${goalMet ? 'text-green-500' : 'text-gray-800'}`}>
                {currentValue} / {goalTarget} {goalLabel}
              </div>
              <div className="text-sm text-gray-500">
                {Math.round(progress * 100)}% of daily goal
              </div>
            </div>
          </div>
          
          {/* Timer */}
          <div className="flex items-center gap-4">
            {timerTarget && (
              <div className="relative">
                <ClockProgress progress={timerProgress} size={60} />
                <div className={`absolute inset-0 flex items-center justify-center text-xs font-medium ${
                  pomodoroComplete ? 'text-green-500' : 'text-gray-600'
                }`}>
                  {pomodoroComplete ? '✓' : ''}
                </div>
              </div>
            )}
            <div className="text-right">
              <div className={`text-xl font-mono ${isPaused ? 'text-yellow-500' : 'text-gray-800'}`}>
                {formatTime(elapsedSeconds)}
              </div>
              <div className="text-xs text-gray-500">
                {timerTarget ? `${timerTarget} min timer` : 'elapsed time'}
              </div>
            </div>
            
            {/* Timer Options */}
            <div className="relative">
              <button
                onClick={() => setShowTimerOptions(!showTimerOptions)}
                className="p-2 rounded-lg hover:bg-gray-100 text-gray-600"
                title="Set timer"
              >
                <Timer size={20} />
              </button>
              {showTimerOptions && (
                <div className="absolute right-0 top-full mt-2 bg-white rounded-lg shadow-lg border border-gray-200 p-2 z-10">
                  <div className="text-xs text-gray-500 mb-2 px-2">Quick timers</div>
                  {[15, 20, 25, 30, 45, 60].map(mins => (
                    <button
                      key={mins}
                      onClick={() => {
                        setPomodoro(mins);
                        setShowTimerOptions(false);
                      }}
                      className="block w-full text-left px-3 py-1 rounded hover:bg-gray-100 text-sm"
                    >
                      {mins} minutes
                    </button>
                  ))}
                  <button
                    onClick={() => {
                      setPomodoro(null);
                      setShowTimerOptions(false);
                    }}
                    className="block w-full text-left px-3 py-1 rounded hover:bg-gray-100 text-sm text-gray-500"
                  >
                    No timer
                  </button>
                </div>
              )}
            </div>
          </div>
          
          {/* Word Stats */}
          <div className="flex gap-4 text-sm">
            <div className="text-center">
              <div className="font-semibold text-gray-800">{stats.words}</div>
              <div className="text-gray-500">words</div>
            </div>
            <div className="text-center">
              <div className="font-semibold text-gray-800">{stats.characters}</div>
              <div className="text-gray-500">chars</div>
            </div>
            {settings.separateCommonWords && (
              <div className="text-center">
                <div className="font-semibold text-gray-800">{stats.contentWords}</div>
                <div className="text-gray-500">content</div>
              </div>
            )}
            <div className="text-center">
              <div className="font-semibold text-gray-800">
                {stats.words > 0 ? Math.round(stats.words / (elapsedSeconds / 60) || 0) : 0}
              </div>
              <div className="text-gray-500">wpm</div>
            </div>
          </div>
          
          {/* Controls */}
          <div className="flex gap-2">
            <button
              onClick={togglePause}
              className={`p-3 rounded-lg transition-colors ${
                isPaused 
                  ? 'bg-yellow-100 text-yellow-600 hover:bg-yellow-200' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
              title={isPaused ? 'Resume' : 'Pause'}
            >
              {isPaused ? <Play size={20} /> : <Pause size={20} />}
            </button>
            <button
              onClick={endSession}
              className="p-3 rounded-lg bg-red-100 text-red-600 hover:bg-red-200 transition-colors"
              title="End session"
            >
              <Square size={20} />
            </button>
          </div>
        </div>
      </div>
      
      {/* Writing Area */}
      <div className="flex-1 bg-white rounded-xl shadow-sm p-4">
        <textarea
          ref={textareaRef}
          value={currentText}
          onChange={(e) => setCurrentText(e.target.value)}
          placeholder="Start writing..."
          className="w-full h-full resize-none text-lg leading-relaxed focus:outline-none"
          style={{ fontFamily: 'Georgia, serif' }}
          disabled={isPaused}
        />
      </div>
      
      {/* Goal Met Notification */}
      {goalMet && (
        <div className="fixed bottom-8 left-1/2 transform -translate-x-1/2 bg-green-500 text-white px-6 py-3 rounded-full shadow-lg flex items-center gap-2 animate-bounce">
          <Check size={20} />
          Goal reached! Keep going or save your work.
        </div>
      )}
    </div>
  );
}

// Stats View Component
function StatsView({ sessions, settings }) {
  const [viewMode, setViewMode] = useState('calendar'); // 'calendar', 'weekly', 'yearly'
  const [selectedMonth, setSelectedMonth] = useState(new Date());
  
  // Get sessions for a specific date
  const getSessionsForDate = (date) => {
    const dateStr = date.toISOString().split('T')[0];
    return sessions.filter(s => s.startTime.split('T')[0] === dateStr);
  };
  
  // Calculate daily totals
  const getDailyTotal = (date) => {
    const daySessions = getSessionsForDate(date);
    return {
      words: daySessions.reduce((sum, s) => sum + s.words, 0),
      minutes: daySessions.reduce((sum, s) => sum + Math.round(s.duration / 60), 0),
      sessions: daySessions.length,
      goalsMet: daySessions.filter(s => s.goalMet).length
    };
  };
  
  // Get week data
  const getWeekData = () => {
    const today = new Date();
    const data = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const total = getDailyTotal(date);
      data.push({
        date,
        dayName: date.toLocaleDateString('en-US', { weekday: 'short' }),
        ...total
      });
    }
    return data;
  };
  
  // Get monthly data for year view
  const getYearData = () => {
    const data = [];
    const currentYear = new Date().getFullYear();
    for (let month = 0; month < 12; month++) {
      const monthSessions = sessions.filter(s => {
        const d = new Date(s.startTime);
        return d.getFullYear() === currentYear && d.getMonth() === month;
      });
      data.push({
        month: new Date(currentYear, month).toLocaleDateString('en-US', { month: 'short' }),
        words: monthSessions.reduce((sum, s) => sum + s.words, 0),
        minutes: monthSessions.reduce((sum, s) => sum + Math.round(s.duration / 60), 0),
        sessions: monthSessions.length,
        goalsMet: monthSessions.filter(s => s.goalMet).length
      });
    }
    return data;
  };
  
  // Calculate overall stats
  const overallStats = {
    totalWords: sessions.reduce((sum, s) => sum + s.words, 0),
    totalMinutes: sessions.reduce((sum, s) => sum + Math.round(s.duration / 60), 0),
    totalSessions: sessions.length,
    goalsMet: sessions.filter(s => s.goalMet).length,
    avgWordsPerSession: sessions.length > 0 ? Math.round(sessions.reduce((sum, s) => sum + s.words, 0) / sessions.length) : 0,
    avgWPM: sessions.length > 0 ? Math.round(sessions.reduce((sum, s) => sum + (s.words / (s.duration / 60)), 0) / sessions.length) : 0
  };
  
  // Calendar days
  const getCalendarDays = () => {
    const year = selectedMonth.getFullYear();
    const month = selectedMonth.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const days = [];
    
    // Add padding for first week
    for (let i = 0; i < firstDay.getDay(); i++) {
      days.push(null);
    }
    
    // Add days of month
    for (let d = 1; d <= lastDay.getDate(); d++) {
      days.push(new Date(year, month, d));
    }
    
    return days;
  };
  
  const weekData = getWeekData();
  const yearData = getYearData();
  const maxWeekWords = Math.max(...weekData.map(d => d.words), 1);
  const maxYearWords = Math.max(...yearData.map(d => d.words), 1);
  
  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 shadow-sm">
          <div className="text-2xl font-bold text-blue-500">{overallStats.totalWords.toLocaleString()}</div>
          <div className="text-sm text-gray-500">Total Words</div>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm">
          <div className="text-2xl font-bold text-green-500">{overallStats.totalMinutes.toLocaleString()}</div>
          <div className="text-sm text-gray-500">Total Minutes</div>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm">
          <div className="text-2xl font-bold text-purple-500">{overallStats.goalsMet}</div>
          <div className="text-sm text-gray-500">Goals Met</div>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm">
          <div className="text-2xl font-bold text-orange-500">{overallStats.avgWPM}</div>
          <div className="text-sm text-gray-500">Avg WPM</div>
        </div>
      </div>
      
      {/* View Toggle */}
      <div className="flex gap-2 justify-center">
        {['calendar', 'weekly', 'yearly'].map(mode => (
          <button
            key={mode}
            onClick={() => setViewMode(mode)}
            className={`px-4 py-2 rounded-lg transition-colors ${
              viewMode === mode 
                ? 'bg-blue-500 text-white' 
                : 'bg-white text-gray-600 hover:bg-gray-100'
            }`}
          >
            {mode.charAt(0).toUpperCase() + mode.slice(1)}
          </button>
        ))}
      </div>
      
      {/* Calendar View */}
      {viewMode === 'calendar' && (
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => setSelectedMonth(new Date(selectedMonth.setMonth(selectedMonth.getMonth() - 1)))}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <ChevronLeft size={20} />
            </button>
            <h3 className="text-lg font-semibold">
              {selectedMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
            </h3>
            <button
              onClick={() => setSelectedMonth(new Date(selectedMonth.setMonth(selectedMonth.getMonth() + 1)))}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <ChevronRight size={20} />
            </button>
          </div>
          
          <div className="grid grid-cols-7 gap-1">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
              <div key={day} className="text-center text-sm text-gray-500 py-2">
                {day}
              </div>
            ))}
            {getCalendarDays().map((date, i) => {
              if (!date) return <div key={`empty-${i}`} />;
              const total = getDailyTotal(date);
              const isToday = date.toDateString() === new Date().toDateString();
              const hasActivity = total.sessions > 0;
              const metGoal = total.goalsMet > 0;
              
              return (
                <div
                  key={date.toISOString()}
                  className={`aspect-square p-1 rounded-lg text-center relative ${
                    isToday ? 'ring-2 ring-blue-500' : ''
                  } ${hasActivity ? (metGoal ? 'bg-green-100' : 'bg-yellow-100') : 'hover:bg-gray-50'}`}
                  title={hasActivity ? `${total.words} words, ${total.minutes} min` : ''}
                >
                  <div className={`text-sm ${isToday ? 'font-bold' : ''}`}>
                    {date.getDate()}
                  </div>
                  {hasActivity && (
                    <div className="text-xs text-gray-600">
                      {total.words}w
                    </div>
                  )}
                </div>
              );
            })}
          </div>
          
          <div className="flex gap-4 mt-4 justify-center text-sm">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-green-100 rounded" />
              <span>Goal met</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-yellow-100 rounded" />
              <span>Wrote (no goal)</span>
            </div>
          </div>
        </div>
      )}
      
      {/* Weekly View */}
      {viewMode === 'weekly' && (
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Last 7 Days</h3>
          <div className="flex items-end justify-between gap-2 h-48">
            {weekData.map((day, i) => (
              <div key={i} className="flex-1 flex flex-col items-center">
                <div 
                  className={`w-full rounded-t-lg transition-all ${
                    day.goalsMet > 0 ? 'bg-green-400' : day.words > 0 ? 'bg-blue-400' : 'bg-gray-200'
                  }`}
                  style={{ height: `${(day.words / maxWeekWords) * 100}%`, minHeight: day.words > 0 ? '4px' : '0' }}
                  title={`${day.words} words, ${day.minutes} min`}
                />
                <div className="text-xs text-gray-500 mt-2">{day.dayName}</div>
                <div className="text-xs font-medium">{day.words > 0 ? day.words : '-'}</div>
              </div>
            ))}
          </div>
          
          {/* Week Summary */}
          <div className="grid grid-cols-3 gap-4 mt-6 pt-4 border-t">
            <div className="text-center">
              <div className="text-xl font-bold text-blue-500">
                {weekData.reduce((sum, d) => sum + d.words, 0).toLocaleString()}
              </div>
              <div className="text-sm text-gray-500">Words this week</div>
            </div>
            <div className="text-center">
              <div className="text-xl font-bold text-green-500">
                {weekData.reduce((sum, d) => sum + d.minutes, 0)}
              </div>
              <div className="text-sm text-gray-500">Minutes this week</div>
            </div>
            <div className="text-center">
              <div className="text-xl font-bold text-purple-500">
                {weekData.filter(d => d.goalsMet > 0).length}/7
              </div>
              <div className="text-sm text-gray-500">Days goal met</div>
            </div>
          </div>
        </div>
      )}
      
      {/* Yearly View */}
      {viewMode === 'yearly' && (
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold mb-4">{new Date().getFullYear()} Overview</h3>
          <div className="flex items-end justify-between gap-2 h-48">
            {yearData.map((month, i) => (
              <div key={i} className="flex-1 flex flex-col items-center">
                <div 
                  className={`w-full rounded-t-lg transition-all ${
                    month.words > 0 ? 'bg-blue-400' : 'bg-gray-200'
                  }`}
                  style={{ height: `${(month.words / maxYearWords) * 100}%`, minHeight: month.words > 0 ? '4px' : '0' }}
                  title={`${month.words} words, ${month.sessions} sessions`}
                />
                <div className="text-xs text-gray-500 mt-2">{month.month}</div>
              </div>
            ))}
          </div>
          
          {/* Year Summary */}
          <div className="grid grid-cols-4 gap-4 mt-6 pt-4 border-t">
            <div className="text-center">
              <div className="text-xl font-bold text-blue-500">
                {yearData.reduce((sum, m) => sum + m.words, 0).toLocaleString()}
              </div>
              <div className="text-sm text-gray-500">Total words</div>
            </div>
            <div className="text-center">
              <div className="text-xl font-bold text-green-500">
                {Math.round(yearData.reduce((sum, m) => sum + m.minutes, 0) / 60)}h
              </div>
              <div className="text-sm text-gray-500">Total hours</div>
            </div>
            <div className="text-center">
              <div className="text-xl font-bold text-purple-500">
                {yearData.reduce((sum, m) => sum + m.sessions, 0)}
              </div>
              <div className="text-sm text-gray-500">Sessions</div>
            </div>
            <div className="text-center">
              <div className="text-xl font-bold text-orange-500">
                {yearData.reduce((sum, m) => sum + m.goalsMet, 0)}
              </div>
              <div className="text-sm text-gray-500">Goals met</div>
            </div>
          </div>
        </div>
      )}
      
      {/* Recent Sessions */}
      <div className="bg-white rounded-xl p-6 shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Recent Sessions</h3>
        {sessions.length === 0 ? (
          <p className="text-gray-500 text-center py-4">No sessions yet. Start writing!</p>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {[...sessions].reverse().slice(0, 20).map(session => (
              <div key={session.id} className="flex items-center justify-between py-2 border-b last:border-0">
                <div>
                  <div className="font-medium">
                    {new Date(session.startTime).toLocaleDateString('en-US', {
                      weekday: 'short',
                      month: 'short',
                      day: 'numeric',
                      hour: 'numeric',
                      minute: '2-digit'
                    })}
                  </div>
                  <div className="text-sm text-gray-500">
                    {session.words} words • {Math.round(session.duration / 60)} min
                  </div>
                </div>
                {session.goalMet && (
                  <div className="bg-green-100 text-green-600 px-2 py-1 rounded text-sm">
                    ✓ Goal met
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Texts View Component
function TextsView({ texts, setTexts }) {
  const [selectedText, setSelectedText] = useState(null);
  const [editingTitle, setEditingTitle] = useState(null);
  const [newTitle, setNewTitle] = useState('');
  
  const deleteText = (id) => {
    if (confirm('Are you sure you want to delete this text?')) {
      setTexts(texts.filter(t => t.id !== id));
      if (selectedText?.id === id) setSelectedText(null);
    }
  };
  
  const updateTitle = (id) => {
    setTexts(texts.map(t => t.id === id ? { ...t, title: newTitle } : t));
    setEditingTitle(null);
  };
  
  const exportText = (text) => {
    const blob = new Blob([`# ${text.title}\n\n${text.content}`], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${text.title.replace(/[^a-z0-9]/gi, '_')}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };
  
  return (
    <div className="grid md:grid-cols-3 gap-4">
      {/* Text List */}
      <div className="md:col-span-1 bg-white rounded-xl shadow-sm p-4">
        <h3 className="font-semibold mb-4">Your Writings ({texts.length})</h3>
        {texts.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No texts saved yet.</p>
        ) : (
          <div className="space-y-2 max-h-[60vh] overflow-y-auto">
            {[...texts].reverse().map(text => (
              <div
                key={text.id}
                onClick={() => setSelectedText(text)}
                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                  selectedText?.id === text.id 
                    ? 'bg-blue-50 border-blue-200 border' 
                    : 'hover:bg-gray-50 border border-transparent'
                }`}
              >
                {editingTitle === text.id ? (
                  <div className="flex gap-2">
                    <input
                      value={newTitle}
                      onChange={(e) => setNewTitle(e.target.value)}
                      className="flex-1 px-2 py-1 border rounded text-sm"
                      onClick={(e) => e.stopPropagation()}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') updateTitle(text.id);
                        if (e.key === 'Escape') setEditingTitle(null);
                      }}
                      autoFocus
                    />
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        updateTitle(text.id);
                      }}
                      className="text-green-500"
                    >
                      <Check size={16} />
                    </button>
                  </div>
                ) : (
                  <>
                    <div className="font-medium truncate">{text.title}</div>
                    <div className="text-xs text-gray-500">
                      {formatDate(text.createdAt)} • {text.wordCount} words
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* Text Preview */}
      <div className="md:col-span-2 bg-white rounded-xl shadow-sm p-6">
        {selectedText ? (
          <>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">{selectedText.title}</h2>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setEditingTitle(selectedText.id);
                    setNewTitle(selectedText.title);
                  }}
                  className="p-2 hover:bg-gray-100 rounded-lg text-gray-600"
                  title="Edit title"
                >
                  <Edit3 size={18} />
                </button>
                <button
                  onClick={() => exportText(selectedText)}
                  className="p-2 hover:bg-gray-100 rounded-lg text-gray-600"
                  title="Export as markdown"
                >
                  <Save size={18} />
                </button>
                <button
                  onClick={() => deleteText(selectedText.id)}
                  className="p-2 hover:bg-red-100 rounded-lg text-red-500"
                  title="Delete"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
            <div className="text-sm text-gray-500 mb-4">
              {new Date(selectedText.createdAt).toLocaleString()} • 
              {selectedText.wordCount} words • 
              {selectedText.characterCount} characters
            </div>
            <div 
              className="prose max-w-none max-h-[50vh] overflow-y-auto"
              style={{ fontFamily: 'Georgia, serif' }}
            >
              {selectedText.content.split('\n').map((para, i) => (
                <p key={i} className="mb-4">{para}</p>
              ))}
            </div>
          </>
        ) : (
          <div className="flex flex-col items-center justify-center h-64 text-gray-500">
            <FileText size={48} className="mb-4 opacity-50" />
            <p>Select a text to view</p>
          </div>
        )}
      </div>
    </div>
  );
}

// Ideas View Component
function IdeasView({ ideas, setIdeas }) {
  const [newIdea, setNewIdea] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState('');
  
  const addIdea = () => {
    if (newIdea.trim()) {
      setIdeas([...ideas, {
        id: Date.now(),
        text: newIdea.trim(),
        createdAt: new Date().toISOString()
      }]);
      setNewIdea('');
    }
  };
  
  const deleteIdea = (id) => {
    setIdeas(ideas.filter(i => i.id !== id));
  };
  
  const updateIdea = (id) => {
    setIdeas(ideas.map(i => i.id === id ? { ...i, text: editText } : i));
    setEditingId(null);
  };
  
  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
        <h3 className="font-semibold mb-4 flex items-center gap-2">
          <Lightbulb className="text-yellow-500" />
          Writing Ideas
        </h3>
        <div className="flex gap-2">
          <input
            type="text"
            value={newIdea}
            onChange={(e) => setNewIdea(e.target.value)}
            placeholder="Add a new idea or topic..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            onKeyDown={(e) => {
              if (e.key === 'Enter') addIdea();
            }}
          />
          <button
            onClick={addIdea}
            disabled={!newIdea.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Plus size={20} />
          </button>
        </div>
      </div>
      
      <div className="bg-white rounded-xl shadow-sm p-6">
        <h3 className="font-semibold mb-4">Your Ideas ({ideas.length})</h3>
        {ideas.length === 0 ? (
          <p className="text-gray-500 text-center py-8">
            No ideas yet. Add something you'd like to write about!
          </p>
        ) : (
          <div className="space-y-2">
            {[...ideas].reverse().map(idea => (
              <div
                key={idea.id}
                className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 group"
              >
                {editingId === idea.id ? (
                  <div className="flex-1 flex gap-2">
                    <input
                      value={editText}
                      onChange={(e) => setEditText(e.target.value)}
                      className="flex-1 px-3 py-1 border rounded-lg"
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') updateIdea(idea.id);
                        if (e.key === 'Escape') setEditingId(null);
                      }}
                      autoFocus
                    />
                    <button
                      onClick={() => updateIdea(idea.id)}
                      className="text-green-500 p-1"
                    >
                      <Check size={18} />
                    </button>
                    <button
                      onClick={() => setEditingId(null)}
                      className="text-gray-500 p-1"
                    >
                      <X size={18} />
                    </button>
                  </div>
                ) : (
                  <>
                    <Lightbulb size={18} className="text-yellow-400 flex-shrink-0" />
                    <span className="flex-1">{idea.text}</span>
                    <span className="text-xs text-gray-400">
                      {formatDate(idea.createdAt)}
                    </span>
                    <div className="opacity-0 group-hover:opacity-100 flex gap-1 transition-opacity">
                      <button
                        onClick={() => {
                          setEditingId(idea.id);
                          setEditText(idea.text);
                        }}
                        className="p-1 hover:bg-gray-200 rounded text-gray-500"
                      >
                        <Edit3 size={16} />
                      </button>
                      <button
                        onClick={() => deleteIdea(idea.id)}
                        className="p-1 hover:bg-red-100 rounded text-red-500"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Settings View Component
function SettingsView({ settings, setSettings }) {
  const updateSetting = (key, value) => {
    setSettings({ ...settings, [key]: value });
  };
  
  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-xl shadow-sm p-6 space-y-6">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Settings className="text-gray-500" />
          Challenge Settings
        </h3>
        
        {/* Goal Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Goal Type
          </label>
          <div className="flex gap-2">
            {[
              { value: 'words', label: 'Words' },
              { value: 'characters', label: 'Characters' },
              { value: 'time', label: 'Time' }
            ].map(opt => (
              <button
                key={opt.value}
                onClick={() => updateSetting('goalType', opt.value)}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  settings.goalType === opt.value
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
        
        {/* Word Goal */}
        {settings.goalType === 'words' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Daily Word Goal
            </label>
            <div className="flex items-center gap-4">
              <input
                type="number"
                value={settings.wordGoal}
                onChange={(e) => updateSetting('wordGoal', parseInt(e.target.value) || 0)}
                className="w-32 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="1"
              />
              <div className="flex gap-2">
                {[250, 500, 750, 1000].map(n => (
                  <button
                    key={n}
                    onClick={() => updateSetting('wordGoal', n)}
                    className={`px-3 py-1 rounded text-sm ${
                      settings.wordGoal === n
                        ? 'bg-blue-100 text-blue-600'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {n}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
        
        {/* Character Goal */}
        {settings.goalType === 'characters' && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Daily Character Goal
              </label>
              <div className="flex items-center gap-4">
                <input
                  type="number"
                  value={settings.characterGoal}
                  onChange={(e) => updateSetting('characterGoal', parseInt(e.target.value) || 0)}
                  className="w-32 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="1"
                />
                <div className="flex gap-2">
                  {[1000, 2500, 5000].map(n => (
                    <button
                      key={n}
                      onClick={() => updateSetting('characterGoal', n)}
                      className={`px-3 py-1 rounded text-sm ${
                        settings.characterGoal === n
                          ? 'bg-blue-100 text-blue-600'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      {n}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="space-y-3">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.countSpaces}
                  onChange={(e) => updateSetting('countSpaces', e.target.checked)}
                  className="w-4 h-4 text-blue-500 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Count spaces</span>
              </label>
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.countPunctuation}
                  onChange={(e) => updateSetting('countPunctuation', e.target.checked)}
                  className="w-4 h-4 text-blue-500 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">Count punctuation</span>
              </label>
            </div>
          </>
        )}
        
        {/* Time Goal */}
        {settings.goalType === 'time' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Daily Time Goal (minutes)
            </label>
            <div className="flex items-center gap-4">
              <input
                type="number"
                value={settings.timeGoal}
                onChange={(e) => updateSetting('timeGoal', parseInt(e.target.value) || 0)}
                className="w-32 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="1"
              />
              <div className="flex gap-2">
                {[15, 20, 25, 30, 45, 60].map(n => (
                  <button
                    key={n}
                    onClick={() => updateSetting('timeGoal', n)}
                    className={`px-3 py-1 rounded text-sm ${
                      settings.timeGoal === n
                        ? 'bg-blue-100 text-blue-600'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {n}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
        
        {/* Separate Common Words */}
        <div>
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={settings.separateCommonWords}
              onChange={(e) => updateSetting('separateCommonWords', e.target.checked)}
              className="w-4 h-4 text-blue-500 rounded focus:ring-blue-500"
            />
            <div>
              <span className="text-sm text-gray-700">Show content words separately</span>
              <p className="text-xs text-gray-500">
                Distinguishes meaningful words from connectors (the, a, and, etc.)
              </p>
            </div>
          </label>
        </div>
        
        {/* Default Pomodoro */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Default Timer Duration (minutes)
          </label>
          <div className="flex items-center gap-4">
            <input
              type="number"
              value={settings.defaultPomodoro}
              onChange={(e) => updateSetting('defaultPomodoro', parseInt(e.target.value) || 25)}
              className="w-32 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              min="1"
            />
          </div>
        </div>
        
        {/* Data Management */}
        <div className="pt-6 border-t">
          <h4 className="font-medium text-gray-700 mb-4">Data Management</h4>
          <div className="flex gap-4">
            <button
              onClick={() => {
                const data = {
                  settings,
                  sessions: JSON.parse(localStorage.getItem('writingSessions') || '[]'),
                  ideas: JSON.parse(localStorage.getItem('writingIdeas') || '[]'),
                  texts: JSON.parse(localStorage.getItem('writingTexts') || '[]')
                };
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `writing-challenge-backup-${new Date().toISOString().split('T')[0]}.json`;
                a.click();
                URL.revokeObjectURL(url);
              }}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Export All Data
            </button>
            <button
              onClick={() => {
                const input = document.createElement('input');
                input.type = 'file';
                input.accept = '.json';
                input.onchange = (e) => {
                  const file = e.target.files[0];
                  const reader = new FileReader();
                  reader.onload = (event) => {
                    try {
                      const data = JSON.parse(event.target.result);
                      if (data.settings) localStorage.setItem('writingSettings', JSON.stringify(data.settings));
                      if (data.sessions) localStorage.setItem('writingSessions', JSON.stringify(data.sessions));
                      if (data.ideas) localStorage.setItem('writingIdeas', JSON.stringify(data.ideas));
                      if (data.texts) localStorage.setItem('writingTexts', JSON.stringify(data.texts));
                      window.location.reload();
                    } catch (err) {
                      alert('Invalid backup file');
                    }
                  };
                  reader.readAsText(file);
                };
                input.click();
              }}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Import Data
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
