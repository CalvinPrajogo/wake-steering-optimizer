# Wind Farm Wake Steering Optimizer

**MIT Energy & Climate Hackathon 2024**

A Python-based tool that uses brute force optimization to find optimal wind turbine yaw angles for maximizing wind farm energy production through wake steering.

## 🎯 Problem Statement

Wind turbines create wakes that reduce the efficiency of downstream turbines by 10-40%. Traditional wind farms leave significant energy on the table due to wake interference.

## 💡 Our Solution

Wake steering optimization software that calculates the optimal yaw angle for each turbine to deflect wakes and maximize total farm power output. By intelligently "steering" wakes away from downstream turbines, we can increase annual energy production by 2-5%.

## 🔬 Technical Approach

- **Wake Modeling**: FLORIS (FLOw Redirection and Induction in Steady State)
- **Optimization**: Brute force search across all yaw angle combinations
- **Configuration**: 4-turbine demonstration (2x2 grid)
- **Yaw Range**: -5° to +5° in 1° increments (14,641 total combinations tested)

## 📊 Key Results

- **Energy Gain**: X.X% increase in total farm power output
- **Optimal Configuration**: Upstream turbines yaw ±X°, downstream at 0°
- **Annual Impact**: +XXX MWh/year additional energy production
- **Revenue Impact**: $XXX,XXX/year additional revenue (@$50/MWh)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/wake-steering-optimizer.git
cd wake-steering-optimizer

# Install dependencies
pip install -r requirements.txt
```

### Usage

```bash
# Run the optimization
python wake_steering_optimizer.py

# This will:
# 1. Test all 14,641 yaw angle combinations
# 2. Find the optimal configuration
# 3. Generate visualizations
# 4. Display results and impact metrics
```

## 📁 Project Structure

```
wake-steering-optimizer/
├── wake_steering_optimizer.py  # Main optimization script
├── visualization.py             # Visualization functions
├── config.py                    # Configuration parameters
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── results/                     # Generated plots and outputs
    ├── flow_comparison.png
    ├── power_comparison.png
    └── optimization_analysis.png
```

## 🛠️ Technology Stack

- **FLORIS**: Wind farm wake modeling and simulation
- **NumPy**: Numerical computations
- **Matplotlib**: Visualization and plotting
- **Pandas**: Data analysis and results management

## 📈 Impact & Scalability

### Demonstrated Impact (4 turbines)
- Power increase: +X.X%
- Computational time: ~XX seconds

### Projected Impact (100MW wind farm)
- Additional annual revenue: $500k - $1.5M
- Pure software solution: Near-zero marginal cost
- Immediate ROI: Implementation cost << 1 year of gains

### Scalability Considerations
- Current: 4 turbines, 11^4 = 14,641 combinations
- Larger farms require smarter optimization (gradient descent, ML)
- Our brute force provides ground truth for validating faster methods

## 🔮 Future Extensions

1. **Machine Learning**: Predict optimal angles from wind conditions
2. **Real-time Integration**: Connect to SCADA systems for live optimization
3. **Multi-objective**: Optimize for power + structural loads
4. **Stochastic Modeling**: Handle variable wind conditions
5. **Larger Farms**: Scale to 50-100+ turbine wind farms

## 🏆 Hackathon Team

- [Your Name]
- [Team Member 2]
- [Team Member 3]
- [Team Member 4]

## 📚 References

- FLORIS: https://github.com/NREL/floris
- Fleming et al. (2019): "Field validation of wake steering"
- Gebraad et al. (2016): "Wind plant power optimization through yaw control"

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- NREL for the FLORIS wake modeling framework
- MIT Energy & Climate Hackathon organizers
- [Any mentors or advisors]

---

**Built with ❤️ at MIT Energy & Climate Hackathon 2024**