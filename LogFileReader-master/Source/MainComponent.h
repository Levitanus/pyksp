

#ifndef MAINCOMPONENT_H_INCLUDED
#define MAINCOMPONENT_H_INCLUDED

#include "../JuceLibraryCode/JuceHeader.h"


class MainContentComponent   : public Component, public Timer, public Button::Listener
{
public:
    //==============================================================================
    MainContentComponent();
    ~MainContentComponent();

    void paint (Graphics&);
    void resized();

	void buttonClicked(Button *buttonThatWasClicked);

	void writeSettingsFile();
	void readSettingsFile();

private:

	class SimpleButton : public TextButton
	{
	public:

		void paintButton(Graphics &g, bool isMouseOverButton, bool isButtonDown) {
			if (getToggleState()) {
				g.fillAll(Colours::whitesmoke);
				if (isMouseOverButton) {
					g.fillAll(Colour(0xffc0c0c0));
				}
			}
			else {
				g.fillAll(Colour(0xff818181));
				if (isMouseOverButton) {
					g.fillAll(Colour(0xffc0c0c0));
				}
			}


			g.setColour(Colours::black);
			Rectangle<int> textBounds(1, 1, getWidth() - 2, getHeight() - 2);
			if (isButtonDown)
			{
				textBounds = Rectangle<int>(2, 2, getWidth() - 2, getHeight() - 2);
			}
			g.drawText(text, textBounds, Justification::centred);
		}

		void setText(String s) { text = s; }

	private:
		String text;

	};

	TextEditor textBox;
	SimpleButton pause;
	SimpleButton autoScroll;
	SimpleButton zoomIn;
	SimpleButton zoomOut;
	SimpleButton fileChooser;
	int fontSize;
	int programWidth;
	int programHeight;
	int64 previousFileSize;
	bool initFlag = true;
	bool setFullscreenFlag = false;
	Rectangle<int> boundsFromSettingsFile;

	void setFontSize(int val);

	String filename;
	Label filenameLabel;
	void setFilenameLabel();

	File getSettingsFile();
	inline const String boolToString(bool b);

	void timerCallback()
	{
		if (pause.getToggleState() == false) {
			
			File logFile(filename);
			if (logFile.exists()) {
				if (logFile.getSize() != previousFileSize)
				{
					String text(logFile.loadFileAsString().trim());

					for (int i = 0; i < 20; i++) {
						text.append("\n",2);
					}
					textBox.setText(text);

					if (autoScroll.getToggleState()) {
						textBox.setScrollToShowCursor(true);
						textBox.setCaretPosition(text.length() - 15);
					}
					else {
						textBox.setScrollToShowCursor(false);
					}
					previousFileSize = logFile.getSize();
				}
			}
			else {
				textBox.setText("LOG FILE READER ERROR: file not found.");
			}
		}

	}



    //==============================================================================
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (MainContentComponent)
};


#endif  // MAINCOMPONENT_H_INCLUDED
