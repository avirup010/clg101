import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import javax.swing.border.*;
import java.text.DecimalFormat;
import javax.swing.plaf.basic.BasicProgressBarUI;
import java.awt.geom.*;

public class BMI_Calculator extends JFrame {
    private JTextField weightField, heightField;
    private JLabel resultLabel, categoryLabel, bmiInfoLabel;
    private JPanel resultPanel, inputPanel;
    private JComboBox<String> unitSelector;
    private CustomProgressBar bmiMeter;
    private Timer colorTransitionTimer;
    private Color currentColor = new Color(66, 133, 244);
    private Color targetColor = new Color(66, 133, 244);

    // UI Constants
    private final Color BACKGROUND_COLOR = new Color(248, 249, 250);
    private final Color PANEL_COLOR = new Color(255, 255, 255);
    private final Color ACCENT_COLOR = new Color(66, 133, 244);
    private final Color TEXT_COLOR = new Color(33, 33, 33);
    private final Color LABEL_COLOR = new Color(95, 99, 104);
    private final Font MAIN_FONT = new Font("Segoe UI", Font.PLAIN, 14);
    private final Font TITLE_FONT = new Font("Segoe UI Light", Font.PLAIN, 28);
    private final Font RESULT_FONT = new Font("Segoe UI", Font.BOLD, 36);
    private final Font INFO_FONT = new Font("Segoe UI", Font.PLAIN, 12);
    
    private final int CORNER_RADIUS = 10;

    public BMI_Calculator() {
        setTitle("BMI Calculator");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout());
        getContentPane().setBackground(BACKGROUND_COLOR);

        // Create main panel with padding
        JPanel containerPanel = new JPanel();
        containerPanel.setLayout(new BoxLayout(containerPanel, BoxLayout.Y_AXIS));
        containerPanel.setBackground(BACKGROUND_COLOR);
        containerPanel.setBorder(new EmptyBorder(25, 25, 25, 25));

        // Rounded panel for content
        JPanel mainPanel = new JPanel() {
            @Override
            protected void paintComponent(Graphics g) {
                Graphics2D g2 = (Graphics2D) g.create();
                g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                g2.setColor(PANEL_COLOR);
                g2.fill(new RoundRectangle2D.Float(0, 0, getWidth(), getHeight(), CORNER_RADIUS, CORNER_RADIUS));
                g2.dispose();
            }
        };
        mainPanel.setLayout(new BoxLayout(mainPanel, BoxLayout.Y_AXIS));
        mainPanel.setBackground(PANEL_COLOR);
        mainPanel.setBorder(new EmptyBorder(25, 25, 25, 25));

        // Title with shadow effect
        JLabel titleLabel = new JLabel("BMI Calculator");
        titleLabel.setFont(TITLE_FONT);
        titleLabel.setForeground(TEXT_COLOR);
        titleLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        // Create fancy unit selector
        unitSelector = createStyledComboBox(new String[]{"Metric (kg, m)", "Imperial (lbs, inches)"});
        unitSelector.setMaximumSize(new Dimension(250, 30));
        unitSelector.setAlignmentX(Component.CENTER_ALIGNMENT);
        unitSelector.addActionListener(e -> calculateBMI());

        // Input panel with rounded corners
        inputPanel = createInputPanel();
        
        // Result panel
        resultPanel = new JPanel();
        resultPanel.setLayout(new BoxLayout(resultPanel, BoxLayout.Y_AXIS));
        resultPanel.setOpaque(false);
        resultPanel.setAlignmentX(Component.CENTER_ALIGNMENT);

        resultLabel = new JLabel("--.-");
        resultLabel.setFont(RESULT_FONT);
        resultLabel.setForeground(ACCENT_COLOR);
        resultLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        categoryLabel = new JLabel("Enter your height and weight");
        categoryLabel.setFont(MAIN_FONT);
        categoryLabel.setForeground(TEXT_COLOR);
        categoryLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        // Custom progress bar for BMI meter
        bmiMeter = new CustomProgressBar(0, 40);
        bmiMeter.setStringPainted(true);
        bmiMeter.setValue(0);
        bmiMeter.setString("");
        bmiMeter.setForeground(ACCENT_COLOR);
        bmiMeter.setBackground(new Color(235, 235, 235));
        bmiMeter.setPreferredSize(new Dimension(250, 20));
        bmiMeter.setMaximumSize(new Dimension(250, 20));
        bmiMeter.setAlignmentX(Component.CENTER_ALIGNMENT);
        
        // BMI information label
        bmiInfoLabel = new JLabel("<html><center>BMI Categories:<br>" +
                                 "Underweight: &lt; 18.5<br>" +
                                 "Normal weight: 18.5 - 24.9<br>" +
                                 "Overweight: 25 - 29.9<br>" +
                                 "Obese: ≥ 30</center></html>");
        bmiInfoLabel.setFont(INFO_FONT);
        bmiInfoLabel.setForeground(LABEL_COLOR);
        bmiInfoLabel.setAlignmentX(Component.CENTER_ALIGNMENT);

        // Add components to result panel
        resultPanel.add(resultLabel);
        resultPanel.add(Box.createRigidArea(new Dimension(0, 10)));
        resultPanel.add(categoryLabel);
        resultPanel.add(Box.createRigidArea(new Dimension(0, 15)));
        resultPanel.add(bmiMeter);
        resultPanel.add(Box.createRigidArea(new Dimension(0, 15)));
        resultPanel.add(bmiInfoLabel);

        // Add components to main panel with proper spacing
        mainPanel.add(titleLabel);
        mainPanel.add(Box.createRigidArea(new Dimension(0, 20)));
        mainPanel.add(unitSelector);
        mainPanel.add(Box.createRigidArea(new Dimension(0, 25)));
        mainPanel.add(inputPanel);
        mainPanel.add(Box.createRigidArea(new Dimension(0, 25)));
        mainPanel.add(resultPanel);

        containerPanel.add(mainPanel);
        add(containerPanel, BorderLayout.CENTER);

        // Initialize color transition timer
        colorTransitionTimer = new Timer(20, new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                if (!currentColor.equals(targetColor)) {
                    currentColor = interpolateColor(currentColor, targetColor, 0.1f);
                    resultLabel.setForeground(currentColor);
                    bmiMeter.setForeground(currentColor);
                    repaint();
                } else {
                    colorTransitionTimer.stop();
                }
            }
        });

        // Set minimum size for responsive layout
        setMinimumSize(new Dimension(350, 600));
        pack();
        setLocationRelativeTo(null);
        
        // Add window listener for smooth opening
        addWindowListener(new WindowAdapter() {
            @Override
            public void windowOpened(WindowEvent e) {
                // Start with zero opacity
                setOpacity(0.0f);
                
                // Create timer for fade-in effect
                Timer fadeInTimer = new Timer(10, new ActionListener() {
                    float opacity = 0.0f;
                    
                    @Override
                    public void actionPerformed(ActionEvent e) {
                        opacity += 0.05f;
                        if (opacity > 1.0f) {
                            opacity = 1.0f;
                            ((Timer)e.getSource()).stop();
                        }
                        setOpacity(opacity);
                    }
                });
                
                fadeInTimer.start();
            }
        });
    }

    private JComboBox<String> createStyledComboBox(String[] items) {
        JComboBox<String> comboBox = new JComboBox<>(items);
        comboBox.setFont(MAIN_FONT);
        comboBox.setBackground(PANEL_COLOR);
        comboBox.setForeground(TEXT_COLOR);
        
        comboBox.setRenderer(new DefaultListCellRenderer() {
            @Override
            public Component getListCellRendererComponent(JList<?> list, Object value, 
                                                         int index, boolean isSelected, 
                                                         boolean cellHasFocus) {
                super.getListCellRendererComponent(list, value, index, isSelected, cellHasFocus);
                setBorder(new EmptyBorder(5, 10, 5, 10));
                return this;
            }
        });
        
        return comboBox;
    }

    private JPanel createInputPanel() {
        JPanel panel = new JPanel();
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
        panel.setOpaque(false);
        panel.setAlignmentX(Component.CENTER_ALIGNMENT);
        panel.setMaximumSize(new Dimension(300, 150));

        // Weight input
        JPanel weightPanel = new JPanel(new BorderLayout(10, 0));
        weightPanel.setOpaque(false);
        JLabel weightLabel = new JLabel("Weight:");
        weightLabel.setFont(MAIN_FONT);
        weightLabel.setForeground(LABEL_COLOR);
        weightField = createStyledTextField();
        weightPanel.add(weightLabel, BorderLayout.WEST);
        weightPanel.add(weightField, BorderLayout.CENTER);

        // Height input
        JPanel heightPanel = new JPanel(new BorderLayout(10, 0));
        heightPanel.setOpaque(false);
        JLabel heightLabel = new JLabel("Height:");
        heightLabel.setFont(MAIN_FONT);
        heightLabel.setForeground(LABEL_COLOR);
        heightField = createStyledTextField();
        heightPanel.add(heightLabel, BorderLayout.WEST);
        heightPanel.add(heightField, BorderLayout.CENTER);

        panel.add(weightPanel);
        panel.add(Box.createRigidArea(new Dimension(0, 15)));
        panel.add(heightPanel);

        // Add input listeners
        weightField.getDocument().addDocumentListener(new SimpleDocumentListener() {
            @Override
            void update() {
                calculateBMI();
            }
        });

        heightField.getDocument().addDocumentListener(new SimpleDocumentListener() {
            @Override
            void update() {
                calculateBMI();
            }
        });

        return panel;
    }

    private JTextField createStyledTextField() {
        JTextField field = new JTextField() {
            @Override
            protected void paintComponent(Graphics g) {
                if (!isOpaque() && getBorder() instanceof RoundedCornerBorder) {
                    Graphics2D g2 = (Graphics2D) g.create();
                    g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                    g2.setColor(getBackground());
                    g2.fill(((RoundedCornerBorder) getBorder()).getBorderShape(
                            0, 0, getWidth() - 1, getHeight() - 1));
                    g2.dispose();
                }
                super.paintComponent(g);
            }
        };
        field.setFont(MAIN_FONT);
        field.setOpaque(false);
        field.setBackground(new Color(245, 245, 245));
        field.setBorder(new RoundedCornerBorder());
        return field;
    }

    private void calculateBMI() {
        try {
            double weight = Double.parseDouble(weightField.getText());
            double height = Double.parseDouble(heightField.getText());

            if (weight <= 0 || height <= 0) throw new NumberFormatException();

            String selectedUnit = (String) unitSelector.getSelectedItem();
            double bmi;

            if ("Imperial (lbs, inches)".equals(selectedUnit)) {
                bmi = (weight / (height * height)) * 703;
            } else {
                bmi = weight / (height * height);
            }

            DecimalFormat df = new DecimalFormat("#.#");
            resultLabel.setText(df.format(bmi));

            String category;
            Color newColor;
            
            if (bmi < 18.5) {
                category = "Underweight";
                newColor = new Color(255, 152, 0);  // Orange
            } else if (bmi < 25) {
                category = "Normal weight";
                newColor = new Color(76, 175, 80);  // Green
            } else if (bmi < 30) {
                category = "Overweight";
                newColor = new Color(255, 152, 0);  // Orange
            } else {
                category = "Obese";
                newColor = new Color(244, 67, 54);  // Red
            }

            categoryLabel.setText(category);
            
            // Animate color change
            targetColor = newColor;
            if (!colorTransitionTimer.isRunning()) {
                colorTransitionTimer.start();
            }
            
            // Animate progress bar
            animateProgressBarTo((int) bmi, df.format(bmi));

        } catch (NumberFormatException e) {
            resultLabel.setText("--.-");
            targetColor = ACCENT_COLOR;
            if (!colorTransitionTimer.isRunning()) {
                colorTransitionTimer.start();
            }
            categoryLabel.setText("Enter valid numbers");
            bmiMeter.setValue(0);
            bmiMeter.setString("");
        }
    }
    
    private void animateProgressBarTo(int targetValue, String displayText) {
        final int startValue = bmiMeter.getValue();
        final int range = targetValue - startValue;
        final int steps = 20;
        
        Timer timer = new Timer(10, null);
        timer.addActionListener(new ActionListener() {
            int step = 0;
            
            @Override
            public void actionPerformed(ActionEvent e) {
                if (step < steps) {
                    float progress = (float)step / steps;
                    // Ease in-out function for smoother animation
                    float easedProgress = (float)(Math.sin((progress - 0.5) * Math.PI) + 1) / 2;
                    int newValue = startValue + Math.round(range * easedProgress);
                    bmiMeter.setValue(newValue);
                    step++;
                } else {
                    bmiMeter.setValue(targetValue);
                    bmiMeter.setString(displayText);
                    timer.stop();
                }
            }
        });
        timer.start();
    }
    
    // Helper method to smoothly transition between colors
    private Color interpolateColor(Color c1, Color c2, float fraction) {
        int red = (int) (c1.getRed() + (c2.getRed() - c1.getRed()) * fraction);
        int green = (int) (c1.getGreen() + (c2.getGreen() - c1.getGreen()) * fraction);
        int blue = (int) (c1.getBlue() + (c2.getBlue() - c1.getBlue()) * fraction);
        return new Color(red, green, blue);
    }

    private abstract class SimpleDocumentListener implements javax.swing.event.DocumentListener {
        abstract void update();

        @Override
        public void insertUpdate(javax.swing.event.DocumentEvent e) {
            update();
        }

        @Override
        public void removeUpdate(javax.swing.event.DocumentEvent e) {
            update();
        }

        @Override
        public void changedUpdate(javax.swing.event.DocumentEvent e) {
            update();
        }
    }
    
    // Custom rounded border for text fields
    private class RoundedCornerBorder extends AbstractBorder {
        private final int radius = 12;
        
        @Override
        public void paintBorder(Component c, Graphics g, int x, int y, int width, int height) {
            Graphics2D g2 = (Graphics2D) g.create();
            g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            g2.setColor(Color.LIGHT_GRAY);
            g2.draw(getBorderShape(x, y, width - 1, height - 1));
            g2.dispose();
        }
        
        public Shape getBorderShape(int x, int y, int width, int height) {
            return new RoundRectangle2D.Double(x, y, width, height, radius, radius);
        }
        
        @Override
        public Insets getBorderInsets(Component c) {
            return new Insets(radius/2, radius, radius/2, radius);
        }
        
        @Override
        public Insets getBorderInsets(Component c, Insets insets) {
            insets.left = radius;
            insets.right = radius;
            insets.top = radius/2;
            insets.bottom = radius/2;
            return insets;
        }
    }
    
    // Custom progress bar with rounded corners
    private class CustomProgressBar extends JProgressBar {
        public CustomProgressBar(int min, int max) {
            super(min, max);
            setUI(new BasicProgressBarUI() {
                @Override
                protected void paintDeterminate(Graphics g, JComponent c) {
                    Graphics2D g2d = (Graphics2D) g.create();
                    g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                    
                    int width = c.getWidth();
                    int height = c.getHeight();
                    int arc = height;
                    
                    // Draw background
                    g2d.setColor(getBackground());
                    g2d.fillRoundRect(0, 0, width, height, arc, arc);
                    
                    // Draw progress
                    int fillWidth = (int) (width * getPercentComplete());
                    g2d.setColor(getForeground());
                    if (fillWidth > 0) {
                        g2d.fillRoundRect(0, 0, fillWidth, height, arc, arc);
                    }
                    
                    // Draw string if painted
                    if (isStringPainted() && getString() != null) {
                        paintString(g2d, 0, 0, width, height, fillWidth, null);
                    }
                    
                    g2d.dispose();
                }
            });
        }
    }

    public static void main(String[] args) {
        try {
            // Try to use FlatLaf if available
            try {
                Class.forName("com.formdev.flatlaf.FlatLightLaf").getMethod("install").invoke(null);
            } catch (ClassNotFoundException e) {
                // Fall back to system look and feel if FlatLaf is not available
                UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        SwingUtilities.invokeLater(() -> {
            new BMI_Calculator().setVisible(true);
        });
    }
}