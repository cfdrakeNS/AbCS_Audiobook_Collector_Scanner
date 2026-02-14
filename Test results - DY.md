abCS with JAWS, NVDA, ZoomText and Windows High Contrast

Overall the app works well with speech using JAWS, NVDA and ZoomText.

Most keyboard commands, quick keys and tabbing work with the following exceptions:



for more investigation  

1\. F1 Help Menu - Cannot tab to the Close button. Not a deal breaker as the Escape key can be used to close the menu. The same applies to the Statistics window.



Fixed 

2\. Book Details window - when the focus is in the Comments edit box, pressing tab or shift+tab will not move to the next or previous field. This needs to be fixed.

\##Fixed Change to ignore tab inside comments field



3\. Alt+E, Selected Count. No response when pressed.

\## field removed was not needed 



Virtualize Window command, Insert+Alt+W, reads the window Title only. However, OCR text in JAWS, Insert+Space, O, W, recognizes all text in the app window.

Read Status Line command, Insert+PageDown, reads the window Title only.



Zoom-in and Zoom-out works well with ZoomText. 

The further you zoom in the text in columns get truncated. The width of the columns can be widened to show more text. However, after resetting zoom, the widened columns do not revert to the original width. 



\##fixed Applied changes need more testing 

\# Fixed content columns - use ResizeToContents so they're always visible

\# Stretch columns use Interactive mode - we control sizing in resizeEvent



I will do some refactoring on fonts, Themes near the end In preferences if you pick default theme it uses your windows default setting for color and highlighting.

The font style of text in the Statistics window should be changed to reflect the font used in the rest of the app.



When Windows 11 High Contrast (LeftAlt+LeftShift+PrintScreen) is enabled to display light coloured text on a black background, line 1 and alternating lines displayed white text on a black background. Alternating lines from line 2 onwards displayed white text on a light-grey background. The same applies to text displayed in the Statistics window. 

In Windows 10, High Contrast changed all text to white text on a black background for all lines in the app.

Text with focus is displayed as black text on a Turquoise Blue background.

The Search edit box, alt+s, displays white text on a grey background, which is more visible than the white text on a light-grey background but still difficult to read.



